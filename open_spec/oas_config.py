from logging import config
import os
from typing import Callable, List
from flask import Flask, current_app
from ._utils import load_file, yaml_dump


class Defaults:
    title = "Title"

    version = "1.0.0"
    debug = False
    validate_on_build = True
    cache_on_build = True
    save_sections_files = True
    auto_build = False
    #
    blueprint_name = "spec_bp"
    blueprint_url_prefix = "/spec"
    register_blueprint = True
    register_json_route = True
    register_ui_route = True
    #
    validate_requests = False
    serialize_response = False
    pre_validattion_handler = None
    post_validattion_handler = None
    #
    json_endpoint = None
    ui_endpoint = None
    #
    root_dir = "."
    final_file_name = "final_oas.yaml"
    oas_dirname = ".oas"
    fragments_dir_name = ".fragments"
    cache_dir_name = ".cache"
    paths_dir_name = "paths"
    override_dir_name = "overrides"
    sections_file_name = "oas_sections.yaml"
    components_file_name = "oas_components.yaml"
    spec_json_url = "/spec"
    spec_ui_url = "/spec-ui"
    ##
    spec_files_locator = None
    use_long_stubs = False
    allowed_methods = [
        "get",
        "post",
        "put",
        "patch",
        "delete",
        "head",
        "options",
        "trace",
        "*",
    ]
    excluded_methods = [
        "head",
        "options",
        "trace",
    ]
    ui_config_url = None
    default_response_mime_type = "application/json"
    #
    update_configs = False


_config_map = {
    "OAS_TITLE": "title",
    "DEBUG": "debug",
    "OAS_VERSION": "version",
    "OAS_VALIDATE_ON_BUILD": "validate_on_build",
    "OAS_CACHE_ON_BUILD": "cache_on_build",
    "OAS_FILE_SAVE": "save_sections_files",
    "OAS_AUTO_BUILD": "auto_build",
    "OAS_VALIDATE_REQUESTS": "validate_requests",
    "OAS_SERIALIZE_RESPONSE": "serialize_response",
    "OAS_PRE_VALIDATION_HANDLER": "pre_validattion_handler",
    "OAS_POST_VALIDATION_HANDLER": "post_validattion_handler",
    "OAS_BLUEPRINT_URL_PREFIX": "blueprint_url_prefix",
    "OAS_BLUEPRINT_NAME": "blueprint_name",
    "OAS_REGISTER_BLUEPRINT": "register_blueprint",
    "OAS_REGISTER_JSON_ROUTE": "register_json_route",
    "OAS_REGISTER_UI_ROUTE": "register_ui_route",
    "OAS_JSON_URL": "spec_json_url",
    "OAS_JSON_ENDPOINT": "json_endpoint",
    "OAS_UI_ENDPOINT": "ui_endpoint",
    "OAS_UI_URL": "spec_ui_url",
    "OAS_ROOT_DIR": "root_dir",
    "OAS_DIR": "oas_dirname",
    "OAS_FRAGMENTS_DIRNAME": "fragments_dir_name",
    "OAS_CACHE_DIRNAME": "cache_dir_name",
    "OAS_SECTIONS_FILENAME": "sections_file_name",
    "OAS_COMPONENTS_FILENAME": "components_file_name",
    "OAS_PATHS_DIR": "paths_dir_name",
    "OAS_FINAL_FILENAME": "final_file_name",
    "OAS_OVERRIDE_FILENAME": "override_dir_name",
    "OAS_LONG_STUB": "use_long_stubs",
    "OAS_SPEC_FILES_LOCATOR": "spec_files_locator",
    "OAS_EXCLUDED_METHODS": "excluded_methods",
    "OAS_ALLOWED_METHODS": "allowed_methods",
    "OAS_UI_CONFIG_URL": "ui_config_url",
    "OAS_DEFAULT_RESPONSE_MIMETYPE": "default_response_mime_type",
    "OAS_UPDATE_CONFIG_YAML": "update_configs",
}


class OasConfig:
    """
    Holds all config values used bu open_spec plugin
    """

    title: str
    version: str
    debug: bool
    validate_on_build: bool
    cache_on_build: bool
    save_sections_files: bool
    auto_build: bool
    blueprint_url_prefix: str  # = "/spec"
    blueprint_name: str  # = "spec_bp"
    register_blueprint: bool  # = True
    #
    validate_requests: bool
    serialize_response: bool
    pre_validattion_handler: Callable
    post_validattion_handler: Callable
    register_json_route: bool
    register_ui_route: bool
    spec_json_url: str
    json_endpoint: str
    ui_endpoint: str
    spec_ui_url: str
    #
    root_dir: str
    oas_dirname: str
    fragments_dir_name: str
    fragments_dir_path: str
    cache_dir_path: str
    cache_dir_name: str
    sections_file_name: str
    sections_file_path: str
    components_file_name: str
    components_file_path: str
    paths_dir_name: str
    paths_dir_path: str
    final_file_name: str
    override_dir_name: str
    #
    use_long_stubs: bool
    #
    spec_files_locator: Callable
    excluded_methods: List
    allowed_methods: List
    #
    ui_config_url: str
    default_response_mime_type: str
    #
    update_configs: bool

    def __init__(self, app: Flask, config_data: dict = {}) -> None:
        with app.app_context():
            src = {}
            if app.config.get("OAS_CONFIG_YAML_SRC", None):
                src = load_file(app.config.get("OAS_CONFIG_YAML_SRC", None))

            src.update(config_data)

            for conf, attr in _config_map.items():
                val = current_app.config.get(
                    conf,
                    src.get(
                        conf,
                        getattr(Defaults, attr, None),
                    ),
                )
                setattr(self, attr, val)

            if self.validate_requests or self.serialize_response:
                self.auto_build = True

            self.allowed_methods = [
                method
                for method in self.allowed_methods
                if method not in self.excluded_methods
            ]

        self.oas_dir_path = os.path.join(self.root_dir, self.oas_dirname)
        self.fragments_dir_path = os.path.join(
            self.oas_dir_path, self.fragments_dir_name
        )

        self.cache_dir_path = os.path.join(
            self.oas_dir_path, self.cache_dir_name
        )
        self.paths_dir_path = os.path.join(
            self.fragments_dir_path, self.paths_dir_name
        )

        self.overrides_dir_path = os.path.join(
            self.oas_dir_path, self.override_dir_name
        )
        self.final_file_path = os.path.join(
            self.oas_dir_path, self.final_file_name
        )
        self.sections_file_path = os.path.join(
            self.fragments_dir_path, self.sections_file_name
        )
        self.components_file_path = os.path.join(
            self.fragments_dir_path, self.components_file_name
        )
        self.sections_files_list = [
            self.sections_file_path,
            self.components_file_path,
        ]

        if self.update_configs:
            file_path = app.config.get("OAS_CONFIG_YAML_SRC", None)
            if not file_path:
                file_path = os.path.join(self.oas_dir_path, "configs.yaml")
            configs = {}
            for conf, attr in _config_map.items():
                val = getattr(
                    self,
                    attr,
                    getattr(Defaults, attr),
                )
                configs[conf] = val
            try:
                os.makedirs(os.path.dirname(file_path))
            except:
                pass
            yaml_dump("", configs, file_path)
