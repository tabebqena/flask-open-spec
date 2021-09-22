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
    blueprint_name = "oas_bp"
    blueprint_url_prefix = "/oas"
    register_blueprint = True
    register_json_route = True
    json_endpoint = "oas_json"
    json_url = "/oas-json"
    register_ui_route = True
    ui_endpoint = "oas_ui"
    ui_url = "/oas-ui"
    #
    validate_requests = False
    authenticate_requests = False
    is_authenticated_handler = None
    on_unauthenticated_handler = None
    default_unauthorized_message = "UNAUTHORIZED"
    pre_validation_handler = None
    post_validation_handler = None
    #
    serialize_response = False
    #
    #
    root_dir = "."
    oas_dirname = ".oas"
    fragments_dir_name = ".fragments"
    paths_dir_name = "paths"
    override_dir_name = "overrides"
    cache_dir_name = ".cache"

    #
    final_file_name = "final_oas.yaml"
    sections_file_name = "oas_sections.yaml"
    components_file_name = "oas_components.yaml"
    ##
    oas_files_locator = None
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
    ui_config_path = None
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
    "OAS_AUTHENTICATE_REQUESTS": "authenticate_requests",
    "OAS_IS_AUTHENTICATED_HANDLER": "is_authenticated_handler",
    "OAS_ON_UNAUTHENTICATED_HANDLER": "on_unauthenticated_handler",
    "OAS_DEFAULT_UNAUTHORIZED_MESSAGE": "default_unauthorized_message",
    "OAS_SERIALIZE_RESPONSE": "serialize_response",
    "OAS_PRE_VALIDATION_HANDLER": "pre_validation_handler",
    "OAS_POST_VALIDATION_HANDLER": "post_validation_handler",
    "OAS_BLUEPRINT_URL_PREFIX": "blueprint_url_prefix",
    "OAS_BLUEPRINT_NAME": "blueprint_name",
    "OAS_REGISTER_BLUEPRINT": "register_blueprint",
    "OAS_REGISTER_JSON_ROUTE": "register_json_route",
    "OAS_REGISTER_UI_ROUTE": "register_ui_route",
    "OAS_JSON_URL": "json_url",
    "OAS_JSON_ENDPOINT": "json_endpoint",
    "OAS_UI_ENDPOINT": "ui_endpoint",
    "OAS_UI_URL": "ui_url",
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
    "OAS_FILES_LOCATOR": "oas_files_locator",
    "OAS_EXCLUDED_METHODS": "excluded_methods",
    "OAS_ALLOWED_METHODS": "allowed_methods",
    "OAS_UI_CONFIG_PATH": "ui_config_path",
    "OAS_DEFAULT_RESPONSE_MIMETYPE": "default_response_mime_type",
    "OAS_UPDATE_CONFIG_YAML": "update_configs",
}


class OasConfig:
    """
     Holds all config values used bu open_oas plugin

     properties:

     title: oas api title
     version: oas api version
     debug: whether to show debug options
     validate_on_build: validate the oas data , raise exception if oas data has error.
     cache_on_build: cache the old files of oas rather than overwriting them.
     save_sections_files: wheather to save the sections file or not, The sections file contain:
        ["openapi", "tags", "externalDocs", "servers", "info"]
     auto_build: if true, open_oas.build() method will be invoked before the first request.
     #
     register_blueprint: register blueprint contains 2 endpoint, one for oas json and the other
        for oas ui.
     blueprint_name: blueprint name. default: oas_bp
     blueprint_url_prefix: url_prefix  argument passed to oas blueprint.
     default : /oas
     register_json_route: register the json route endpoint or not.
     default is True
     json_endpoint: default: oas_json
     json_url: the url for the oas json route. default: /oas-json
     register_ui_route: register the ui route endpoint or not.
     default is True
     ui_endpoint: The endpoint of the ui route. default: oas_ui
     ui_url: The url for the ui_endpoint default: ui_url
     #
     validate_requests: validate incoming requests by the provided schema in `requestBody` attr
      of the corresponding `paths`:`path`:`method`
      if the request invalid: it will be aborted with data containing errors
     pre_validation_handler:
       function of no arguments, will be called before validating the request.
       If any exception raised, the validation process will be aborted.
       default is None

     post_validation_handler:
       function of no arguments, will be called after validating the request.
       default is None
     authenticate_requests: apply the security schemes provided by oas for each request.
       if the request is unauthenticated, on_unauthenticated_handler will be called.
       if `on_unauthenticated_handler` is None, default handler will be called. default handler
       will return response by 401 status code and message equals to `default_unauthorized_message`

     on_unauthenticated_handler: handler will be called if the request is unauthenticated.

     is_authenticated_handler: global handler that will be called for each response to check whether
     it is authenticated or not. Each `securitySchemes` in `oas.components` can has its specific handler
     definded by `x-handler` attribute, This attribute can accept the qual name of the handler function.
     If the schema has no value of `x-handler` attribute, This global handler will be applied.
     handler function should accept at 2 args at least: scheme which is the security scheme required for current request.
     and info which is the data parsed from the request according to the scheme specification.
     default : None

     default_unauthorized_message: message be used by on_unauthenticated_handler.
     #
     serialize_response: wheather to serialize reponses by the specified `responses` key in `paths`.`path`.`method`.

     default is None
     default_response_mime_type: default value used if the responses object not containing the required mimetype.
     default: application/json
     #
    root_dir: The root dir of the app, it is  preferred to supply this option.
    oas_dirname: name of the `oas_dir` subdirectory of the root_dir that  will contain the oas files. default = ".oas"
    fragments_dir_name:  name of the `fragments` dir, it is subdirectory of the `oas_dir`. it will contain the paths,
         components and sections files.
     default: .fragments
    paths_dir_name: name of the `paths` dir, subdirectory of the `oas`dir that will contain the `paths` data.
     default: paths
    override_dir_name: name of the `overrides` dir, sudirectory of the `oas`dir that will contain the overrides.yaml files.
    default = "overrides"
    cache_dir_name: name of the `cache` dir, subdirectory of the `oas` dir that will contain the cached files if `cache_on_build` is True
    sections_file_name: The name of the sections file, This file will contain the data for:
        ["openapi", "tags", "externalDocs", "servers", "info"]
        default : oas_sections.yaml
    components_file_name:  The name of the components file.
        default : oas_components.yaml
    final_file_name: The name of the file that will contain whole oas data after processing it.
    default: final_oas.yaml

    use_long_stubs: use long templates instead of short ones.
    default: False

    oas_files_locator: Optional function used to detect the corresponding oas file path of each flask route.
    This function should accept 2 keyword arguments: rule, path and should return the full path of the corresponding oas file.

    excluded_methods: list of methods to exclude from the oas file.
    default:  ["head",
        "options",
        "trace",]
    allowed_methods: list of methods to include in the oas file.
    #
    ui_config_path: path to the yaml file that contains the config of the SwaggerUI object.
    #
    update_configs: Update the yaml config file by the processed configs from this class.
    The yaml config file path is supplied seperately by:  app.config["OAS_CONFIG_YAML_SRC"]

    """

    title: str
    version: str
    debug: bool
    validate_on_build: bool
    cache_on_build: bool
    save_sections_files: bool
    auto_build: bool
    #
    register_blueprint: bool  # = True
    blueprint_name: str  # = "spec_bp"
    blueprint_url_prefix: str  # = "/spec"
    register_json_route: bool
    register_ui_route: bool
    json_url: str
    json_endpoint: str
    ui_endpoint: str
    ui_url: str
    #
    validate_requests: bool
    # TODO: on_invalid _request_handler
    pre_validation_handler: Callable
    post_validation_handler: Callable
    #
    authenticate_requests: bool
    is_authenticated_handler: Callable
    on_unauthenticated_handler: Callable
    default_unauthorized_message: str
    #
    serialize_response: bool
    default_response_mime_type: str
    #
    root_dir: str
    oas_dirname: str
    fragments_dir_name: str
    # fragments_dir_path: str
    override_dir_name: str

    # cache_dir_path: str
    cache_dir_name: str
    sections_file_name: str
    # sections_file_path: str
    components_file_name: str
    # components_file_path: str
    paths_dir_name: str
    # paths_dir_path: str
    final_file_name: str
    #
    use_long_stubs: bool
    #
    oas_files_locator: Callable
    excluded_methods: List
    allowed_methods: List
    #
    ui_config_path: str
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
