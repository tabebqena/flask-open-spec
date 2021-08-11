import os
from pprint import pprint
from typing import Callable, cast

import click
from flask import Flask
from openapi_spec_validator import validate_spec

from .__cli_wrapper import __CliWrapper, _OpenSpec__CliWrapper  # noqa
from .__loader import __load_data, _OpenSpec__load_data  # noqa
from .__spec_wrapper import _get_spec_dict
from .__view import __ViewManager, _OpenSpec__ViewManager  # noqa
from .__validator import (
    __RequestsValidator,
    _OpenSpec__RequestsValidator,
)  # noqa
from ._editor import TemplatesEditor
from ._parameters import get_app_paths
from ._utils import cache_file, clean_data, merge_recursive, yaml_dump
from .oas_config import OasConfig


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
        self._app_paths = {}
        self.row_data = {}
        self.final_oas = {}

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
        self.__view_manager = __ViewManager(
            self,
            blueprint_name=blueprint_name,
            url_prefix=url_prefix,
            auto_build=auto_build,
            authorization_handler=authorization_handler,
        )
        if self.config.validate_requests:
            self.__requests_validator = __RequestsValidator(self)

    def init(self, echo=True):
        self._app_paths = get_app_paths()
        self.__editor = TemplatesEditor(self, echo)
        # self.__editor.init(echo)

    def build(self, validate=None, cache=None):
        self.init(echo=False)
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
        self.row_data = __load_data(self.config, self.__editor)
        # pprint(self.row_data)
        spec_data = _get_spec_dict(cast(dict, self.row_data), self.config)
        data = clean_data(
            merge_recursive(
                [
                    spec_data,
                    self.row_data,
                ]
            )
        )
        if cached_final and not cache:
            os.remove(cached_final)
        if validate:
            validate_spec(data)
        yaml_dump("", data, file=self.config.final_file)
        self.final_oas = data
        if self.config.debug:
            click.echo(self.config.final_file)

    def get_spec_dict(self):
        return self.__view_manager.get_spec_dict()

    def get_spec_json(self):
        return self.__view_manager.get_spec_json()

    def get_spec_ui(self):
        return self.__view_manager.get_spec_ui()
