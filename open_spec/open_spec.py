from copy import deepcopy
from .oas_config import OasConfig
import os
from typing import Callable, Optional, cast

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
from ._editor import TemplatesEditor
from ._utils import (
    cache_file,
    clean_data,
    clean_parameters_list,
    load_file,
    merge_recursive,
    remove_none,
    yaml_dump,
)
from ._parameters import get_app_paths
from .__cli_wrapper import __CliWrapper, _OpenSpec__CliWrapper  # noqa
from .__view import __ViewManager, _OpenSpec__ViewManager  # noqa
from .__loader import __load_data, _OpenSpec__load_data  # noqa
from .__spec_wrapper import _get_spec_dict


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
        self.__editor = TemplatesEditor(self.config)

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
            self.__editor.__update_all()
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
        data = __load_data(self.config, self.__editor)
        #print(137, data["paths"]["/gists/{gist_id}"]["put"]["requestBody"])
        spec_data = _get_spec_dict(cast(dict, data), self.config)
        #
        data = clean_data(
            merge_recursive(
                [
                    spec_data,
                    data,
                ]
            )
        )
        if cached_final and not cache:
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
