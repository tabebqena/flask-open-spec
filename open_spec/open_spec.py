import os
from typing import Callable

import click
from flask import Flask
from flask.cli import AppGroup
from openapi_spec_validator import validate_spec

from .__loader import __load_data, _OpenSpec__load_data  # noqa
from .consumer.__serializer import (  # noqa
    __ResponseSerializer,
    _OpenSpec__ResponseSerializer,
)  # noqa
from .consumer.__validator import (  # noqa
    __RequestsValidator,
    _OpenSpec__RequestsValidator,
)  # noqa
from .__view import __ViewManager, _OpenSpec__ViewManager  # noqa
from ._editor import TemplatesEditor
from ._parameters import get_app_paths
from ._utils import cache_file, yaml_dump
from .oas_config import OasConfig
from ._editor import make_template_data


def set_cli(open_spec: "OpenSpec"):
    oas_cli = AppGroup(
        "oas",
        help="command line interface to control OAS of flask app and marshmallow schemas\n \
                    This tool can help by generating stub files, and merging them to form the OAS file",
    )

    @oas_cli.command(
        "build",
        help="Extract data from all marshmallow schemas, add them in the right place, \n \
            merge all files from .generated dir in one file and apply overrides if present in overrides file.",
    )
    @click.option("--validate", type=bool, default=True)
    @click.option("--cache", type=bool, default=True)
    def build(validate, cache):
        open_spec.build(validate=validate, cache=cache)

    open_spec.app.cli.add_command(oas_cli)


class OpenSpec:
    def __init__(
        self,
        app: Flask = None,
        oas_data: dict = {},
        blueprint_name: str = None,
        url_prefix: str = None,
        auto_build=None,
        authorization_handler: Callable = None,
        config_data: dict = {},
        config_obj: OasConfig = None,
    ) -> None:
        self._app_paths = {}
        self.input_oas_data = oas_data
        self.oas_data = {}

        if app:
            self.init_app(
                app,
                blueprint_name,
                url_prefix,
                auto_build,
                authorization_handler,
                config_data,
                config_obj=config_obj,
            )

    def init_app(
        self,
        app: Flask,
        blueprint_name: str = None,
        url_prefix: str = None,
        auto_build=None,
        authorization_handler: Callable = None,
        config_data: dict = {},
        config_obj: OasConfig = None,
    ):
        self.app = app
        if config_obj:
            self.config: OasConfig = config_obj
        else:
            self.config: OasConfig = OasConfig(app, config_data)
        #
        self.__view_manager = __ViewManager(
            self,
            blueprint_name=blueprint_name,
            url_prefix=url_prefix,
            auto_build=True,  # auto_build, # should be always True
            authorization_handler=authorization_handler,
        )
        if self.config.validate_requests:
            __RequestsValidator(self)
        if self.config.serialize_response:
            __ResponseSerializer(self)
        #
        set_cli(self)
        self.app.extensions["open_spec"] = self

    def build(self, validate=None, cache=None):
        self._app_paths = get_app_paths()
        template_data = make_template_data(self.config, self._app_paths)
        self._editor = TemplatesEditor(self, template_data, False)

        if validate is None:
            validate = self.config.validate_on_build
        cached_final = None
        if cache is None:
            cache = self.config.cache_on_build
            if cache:
                cached_final = cache_file(
                    self.config.final_file_path,
                    self.config.oas_dir_path,
                    self.config.cache_dir_path,
                )

        data = __load_data(
            self, self._editor.template_data, self.input_oas_data
        )
        if cached_final and not cache:
            os.remove(cached_final)
        if validate:
            validate_spec(data)
        yaml_dump("", data, file=self.config.final_file_path)
        self.oas_data = data
        if self.config.debug:
            click.echo(self.config.final_file_path)

    def get_spec_dict(self):
        return self.__view_manager.get_spec_dict()

    def get_spec_json(self):
        return self.__view_manager.get_spec_json()

    def get_spec_ui(self):
        return self.__view_manager.get_spec_ui()
