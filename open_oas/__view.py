import json
import os
from typing import TYPE_CHECKING

from flask import Blueprint, current_app, jsonify, render_template, url_for
from ._utils import load_file, cache_file

if TYPE_CHECKING:
    from .open_oas import OpenOas


class __ViewManager:
    def __init__(
        self,
        open_oas: "OpenOas",
        blueprint_name="",
        url_prefix=None,
        auto_build=False,
        authorization_handler=None,
    ) -> None:
        self.open_oas = open_oas
        self.app = open_oas.app

        self.config = open_oas.config
        self.__auto_build_flag = auto_build
        self.__authorization_handler = authorization_handler
        self.__blueprint_name = blueprint_name or self.config.blueprint_name
        self.__url_prefix = url_prefix or self.config.blueprint_url_prefix

        self.__register_callback()
        self.__register_spec_blueprint()
        self.__built = True

    def __auto_build(self):
        try:
            cached_final = cache_file(
                self.config.final_file_path,
                self.config.oas_dir_path,
                self.config.cache_dir_path,
            )

            self.open_oas.build()
            if cached_final and os.path.exists(cached_final):
                os.remove(cached_final)
        except Exception as e:
            current_app.logger.warning(e, e.__traceback__)

    def __register_callback(self):
        auto_build = (
            lambda res: self.__auto_build_flag
            if self.__auto_build_flag is not None
            else self.config.auto_build
        )

        if auto_build:
            self.app.before_first_request(self.__auto_build)

    def __register_spec_blueprint(self):
        if not self.config.register_blueprint:
            return
        self.blueprint = Blueprint(
            self.__blueprint_name,
            __name__,
            template_folder="./templates",
            static_folder="static",
            static_url_path="/static",
            url_prefix=self.__url_prefix,
        )

        if self.config.register_json_route:
            self.blueprint.add_url_rule(
                self.config.json_url,
                view_func=self.get_spec_json,
                endpoint=self.config.json_endpoint or "oas_json",
            )

        self.ui_config_path = self.config.ui_config_path

        if self.config.register_ui_route:
            self.blueprint.add_url_rule(
                self.config.ui_url,
                view_func=self.get_spec_ui,
                endpoint=self.config.ui_endpoint or "oas_ui",
            )
        self.app.register_blueprint(self.blueprint)

    def get_ui_config(self):
        return load_file(
            self.config.ui_config_path
            or url_for(
                self.__blueprint_name + ".static", filename="ui_config.yaml"
            )
        )

    def get_spec_dict(self):
        if not self.__built:
            self.open_oas.build()
            self.__built = True

        return load_file(self.config.final_file_path)

    def get_spec_json(self):
        if self.__authorization_handler:
            self.__authorization_handler()

        return jsonify(self.get_spec_dict())

    def get_spec_ui(self):
        ui_config_path = self.config.ui_config_path
        if not ui_config_path or not os.path.exists(ui_config_path):
            ui_config_path = os.path.join(
                os.path.dirname(__file__), "static", "ui_config.yaml"
            )
        return render_template(
            "swagger-ui.html",
            blueprint_name=self.blueprint.name,
            json_url=url_for(
                self.config.json_endpoint
                or self.__blueprint_name + ".get_spec_json"
            ),
            config_url=url_for(
                self.__blueprint_name + ".static",
                filename="ui_config.yaml"
                # self.__blueprint_name + ".static",
                # filename="ui_config.json",
            ),
            config_data=json.dumps(load_file(ui_config_path)),
        )


_OpenOas__ViewManager = __ViewManager
