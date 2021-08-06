from copy import deepcopy
from .oas_config import OasConfig
import os
from typing import Callable, Optional

import click
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import (
    Blueprint,
    Flask,
    current_app,
    jsonify,
    render_template,
    url_for,
)
from openapi_spec_validator import validate_spec

from .builder import OasBuilder
from ._editor import Editor
from ._utils import (
    cache_file,
    clean_data,
    clean_parameters_list,
    load_file,
    merge_recursive,
    remove_none,
    yaml_dump,
)
from ._parameters import get_app_paths, extract_path_parameters
from .__cli_wrapper import __CliWrapper, _OpenSpec__CliWrapper
from .__view import __ViewManager, _OpenSpec__ViewManager


def _add_paths_to_spec(spec: APISpec, data):
    app_paths_list = get_app_paths()

    for path in app_paths_list:
        for method in app_paths_list[path]:

            summary: str = data.get("paths", {}).get(path, {}).get("summary")
            description: str = (
                data.get("paths", {}).get(path, {}).get("description")
            )
            parameters = clean_parameters_list(
                data.get("paths", {}).get(path, {}).get("parameters", [])
            )
            operation = (
                data.get("paths", {}).get(path, {}).get(method, {}) or {}
            )
            if operation and operation.get("responses", {}):
                operation["responses"] = remove_none(
                    operation.get("responses", {})
                )
            if operation and operation.get("requestBody", {}):
                operation["requestBody"] = remove_none(
                    operation.get("requestBody", {})
                )
            if operation and operation.get("parameters", {}):
                operation["parameters"] = clean_parameters_list(
                    operation.get("parameters", [])
                )
            spec.path(
                path,
                summary=summary,
                description=description,
                parameters=parameters,
                operations={method: operation},
            )


def _clean_invalid_paths(data):
    app_paths_list = get_app_paths()
    data_paths = deepcopy(data.get("paths", {}))
    keys = data.get("paths", {}).keys()
    for path in keys:
        if path not in app_paths_list:
            del data_paths[path]
    data["paths"] = data_paths
    return data


def _load_or_fetch(save_files, file_path, fetcher, fetcher_kwargs={}):
    if save_files:
        return load_file(file_path)
    return fetcher(**fetcher_kwargs)


class OpenSpec:
    
    def __init__(
        self,
        app: Flask = None,
        blueprint_name: str = None,
        url_prefix: str = None,
        auto_build=None,
        authorization_handler: Callable = None,
        config_obj: OasConfig = None,
    ) -> None:

        if app:
            self.init_app(
                app,
                blueprint_name,
                url_prefix,
                auto_build,
                authorization_handler,
                config_obj,
            )

    def init_app(
        self,
        app: Flask,
        blueprint_name: str = None,
        url_prefix: str = None,
        auto_build=None,
        authorization_handler: Callable = None,
        config_obj: OasConfig = None,
    ):
        self.app = app

        if config_obj:
            self.config: OasConfig = config_obj
        else:
            self.config: OasConfig = OasConfig(app)

        __CliWrapper(self)
        self.view_manager = __ViewManager(
            self,
            blueprint_name=blueprint_name,
            url_prefix=url_prefix,
            auto_build=auto_build,
            authorization_handler=authorization_handler,
        )
        self.__editor = Editor(self.config)

    def __run_updaters(self):
        self.__editor.upadte_draft_file()
        self.__editor.upadte_paths_details_file()

        self.__editor.update_path_parameters()
        self.__editor.update_request_file()
        self.__editor.update_responses_file()

    def init_command(self, echo=True):
        try:
            os.makedirs(self.config.oas_dir)
        except:
            pass
        if self.config.save_files:
            try:
                os.makedirs(self.config.fragments_dir)
            except Exception as e:
                pass

            for f in self.config.files_list:
                if not os.path.exists(f):
                    open(f, "w").close()
            self.__run_updaters()
            if echo and self.config.debug:
                click.echo(
                    "Now, It is your time to edit the generated files:\
                        \n - {0}\n - {1}\n - {2}\n - {3}\n - {4}\n ".format(
                        self.config.draft_file,
                        self.config.parameters_file,
                        self.config.request_body_file,
                        self.config.responses_file,
                        self.config.override_file,
                    )
                )
        else:
            if not os.path.exists(self.config.override_file):
                open(self.config.override_file, "w").close()
            if echo and self.config.debug:

                click.echo(
                    "- generated files:\
                        \n - {0}\n ".format(
                        self.config.override_file,
                    )
                )
        self.__editor.update_snippets_files()

    def __make_spec(self, data):
        spec = APISpec(
            title=data.get("info", {}).get("title", self.config.title),
            version=data.get("info", {}).get("version", self.config.version),
            openapi_version="3.0.2",
            info=data.get("info", {}),
            plugins=[MarshmallowPlugin()],
        )
        return spec

    def __load_data(self):
        draft_data = load_file(self.config.draft_file)
        paths_details = _load_or_fetch(
            self.config.save_files,
            self.config.paths_file,
            self.__editor.extract_paths_details,
        )
        parameters = _load_or_fetch(
            self.config.save_files,
            self.config.parameters_file,
            extract_path_parameters,
            {
                "long_stub": self.config.use_long_stubs,
                "allowed_methods": self.config.allowed_methods,
            },
        )
        requestBodies = _load_or_fetch(
            self.config.save_files,
            self.config.request_body_file,
            self.__editor.extract_request_bodies,
        )

        responses = _load_or_fetch(
            self.config.save_files,
            self.config.responses_file,
            self.__editor.extract_responses,
        )
        overrides = load_file(self.config.override_file)
        spec_files_data = self.__editor.load_snippet_files()

        #
        data = merge_recursive(
            [
                overrides,
                # decorators_data,
                OasBuilder.data,
                spec_files_data,
                paths_details,
                parameters,
                requestBodies,
                responses,
                draft_data,
            ]
        )

        data = _clean_invalid_paths(data)
        return data

    def build_command(self, validate=None, cache=None):
        self.init_command(echo=False)
        if validate is None:
            validate = self.config.validate_on_build
        cached_final = None
        if cache is None:
            cache = self.config.cache_on_build
            if cache:
                cached_final = cache_file(
                    self.config.final_file,
                    self.config.oas_dir,
                    self.config.cache_dir,
                )
        data = self.__load_data()

        spec = self.__make_spec(data)
        _add_paths_to_spec(spec, data)

        data = clean_data(
            merge_recursive(
                [
                    spec.to_dict(),
                    data,
                ]
            )
        )
        if cached_final:
            os.remove(cached_final)
        if validate:
            validate_spec(data)
        yaml_dump("", data, file=self.config.final_file)
        if self.config.debug:
            click.echo(self.config.final_file)
        # store data in snippets
        self.__editor.update_snippets_files()

    def get_spec_dict(self):
        return self.view_manager.get_spec_dict()

    def get_spec_json(self):
        return self.view_manager.get_spec_json()

    def get_spec_ui(self):
        return self.view_manager.get_spec_ui()
