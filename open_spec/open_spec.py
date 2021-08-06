from copy import deepcopy
from .oas_config import OasConfig
import os
from logging import warning
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
from flask.cli import AppGroup
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


class CliWrapper:
    def __init__(self, open_spec_obj) -> None:
        self.oas_cli = oas_cli = AppGroup(
            "oas",
            help="command line interface to control OAS of flask app and marshmallow schemas\n \
                    This tool can help by generating stub files, and merging them to form the OAS file",
        )

        @oas_cli.command(
            "init",
            help="Generate files from stubs, If file already present, It will merged with the stub data \n \
        Always consider revising the generated files. and caching the previous versions.",
        )
        @click.option(
            "-o",
            "--document-options",
            is_flag=True,
            default=None,
            is_eager=True,
        )
        def init(document_options=None):
            open_spec_obj.init_command(document_options=document_options)

        @oas_cli.command(
            "build",
            help="Extract data from all marshmallow schemas, add them in the right place, \n \
            merge all files from .generated dir in one file and apply overrides if present in overrides file.",
        )
        @click.option("--validate", type=bool, default=True)
        @click.option("--cache", type=bool, default=True)
        def build(validate, cache):
            open_spec_obj.build_command(validate=validate, cache=cache)

        # @click.option(
        #    "-o",
        #    "--document-options",
        #    is_flag=True,
        #    default=None,
        # )  # is_eager=True,
        open_spec_obj.app.cli.add_command(oas_cli)


def _add_paths_to_spec(spec: APISpec, data):
    Aapp_paths_list = get_app_paths()

    for path in Aapp_paths_list:
        for method in Aapp_paths_list[path]:
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


def _load_or_fetch(save_files, file_path, fetcher):
    if save_files:
        return load_file(file_path)
    return fetcher()


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
        self.__built = False
        self.__url_prefix = url_prefix
        self.__auto_build_flag = auto_build
        self.__authorization_handler = authorization_handler

        if app:
            self.init_app(app, blueprint_name, config_obj)

    def init_app(
        self,
        app: Flask,
        blueprint_name=None,
        config_obj: Optional[OasConfig] = None,
    ):
        self.app = app
        CliWrapper(self)
        self.__register_callback()

        if config_obj:
            self.config: OasConfig = config_obj
        else:
            self.config: OasConfig = OasConfig(app)
        self.__blueprint_name = blueprint_name or self.config.blueprint_name

        self.__editor = Editor(self.config)
        self.register_spec_blueprint(
            blueprint_name=self.__blueprint_name, url_prefix=self.__url_prefix
        )
        self.app.extensions["open_spec"] = self

    def __auto_build(self):
        cached_final = cache_file(
            self.config.final_file, self.config.oas_dir, self.config.cache_dir
        )
        try:
            self.build_command()
            if cached_final and os.path.exists(cached_final):
                os.remove(cached_final)
        except Exception as e:
            warning(e)

    def __register_callback(self):
        auto_build = (
            lambda res: self.__auto_build_flag
            if self.__auto_build_flag is not None
            else self.config.auto_build
        )

        if auto_build:
            self.app.before_first_request(self.__auto_build)

    def __run_updaters(self, document_options):
        self.__editor.upadte_draft_file()
        self.__editor.upadte_paths_details_file()

        self.__editor.update_path_parameters(document_options)
        self.__editor.update_request_file(document_options)
        self.__editor.update_responses_file(document_options)

    def init_command(self, document_options=None, echo=True):
        if document_options is None:
            document_options = self.config.document_options
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
            self.__run_updaters(document_options)
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
        paths = _load_or_fetch(
            self.config.save_files,
            self.config.paths_file,
            self.__editor.extract_paths_details,
        )
        parameters = _load_or_fetch(
            self.config.save_files,
            self.config.parameters_file,
            extract_path_parameters,
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
        data = merge_recursive(
            [
                overrides,
                OasBuilder.data,
                paths,
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
        self.__built = True
        yaml_dump("", data, file=self.config.final_file)
        if self.config.debug:
            click.echo(self.config.final_file)

    def register_spec_blueprint(self, blueprint_name=None, url_prefix=None):
        if not self.config.register_blueprint:
            return
        if not url_prefix:
            url_prefix = self.config.blueprint_url_prefix
        if not blueprint_name:
            blueprint_name = self.config.blueprint_name
        self.blueprint = Blueprint(
            blueprint_name,
            __name__,
            template_folder="./templates",
            static_folder="static",
            static_url_path="/static",
            url_prefix=url_prefix,
        )

        if self.config.register_json_route:
            self.blueprint.add_url_rule(
                self.config.spec_json_url,
                view_func=self.get_spec_json,
                endpoint=self.config.json_endpoint or "get_spec_json",
            )

        if self.config.register_ui_route:
            self.blueprint.add_url_rule(
                self.config.spec_ui_url,
                view_func=self.get_spec_ui,
                endpoint=self.config.ui_endpoint or "get__spec_ui",
            )
        self.app.register_blueprint(self.blueprint)

    def get_spec_dict(self):
        if not self.__built:
            self.build_command()

        return load_file(self.config.final_file)

    def get_spec_json(self):
        if self.__authorization_handler:
            self.__authorization_handler()

        return jsonify(self.get_spec_dict())

    def get_spec_ui(self):

        return render_template(
            "swagger-ui.html",
            blueprint_name=self.blueprint.name,
            json_url=url_for(
                self.config.json_endpoint
                or self.__blueprint_name + ".get_spec_json"
            ),
        )
