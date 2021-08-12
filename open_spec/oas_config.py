import os
from flask import Flask, current_app


class OasConfig:
    title: str
    version = "1.0.0"
    debug = False
    validate_on_build = True
    cache_on_build = True
    save_sections_files = True
    auto_build = False
    blueprint_url_prefix = "/spec"
    blueprint_name = "spec_bp"
    validate_requests = False
    pre_validattion_handler = None

    __register_blueprint = True
    __register_json_route = True
    __register_ui_route = True

    root_dir = "."
    __final_file_name = "final_oas.yaml"
    __oas_dirname = ".oas"
    __fragments_dir = ".fragments"
    __cache_dir = ".cache"
    __paths_details_dir = "paths"
    __override_file_name = "override_oas.yaml"
    __oas_sections_file_name = "oas_sections.yaml"
    __spec_json_url = "/spec"
    __spec_ui_url = "/spec-ui"
    __spec_files_locator = None
    __use_long_stubs = False
    __allowed_methods = [
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
    __excluded_methods = [
        "head",
        "options",
        "trace",
    ]
    __ui_config_url = None

    def __init__(self, app: Flask) -> None:
        with app.app_context():
            self.title = current_app.config.get("OAS_TITLE", app.name)
            self.version = current_app.config.get("OAS_VERSION", self.version)
            self.debug = current_app.debug

            self.validate_on_build = current_app.config.get(
                "OAS_VALIDATE_ON_BUILD", self.validate_on_build
            )
            self.cache_on_build = current_app.config.get(
                "OAS_CACHE_ON_BUILD", self.cache_on_build
            )
            self.save_sections_files = current_app.config.get(
                "OAS_FILE_SAVE", True
            )
            self.auto_build = current_app.config.get("OAS_AUTO_BUILD", False)
            self.validate_requests = current_app.config.get(
                "OAS_VALIDATE_REQUESTS", False
            )
            if self.validate_requests:
                self.auto_build = True

            self.pre_validattion_handler = current_app.config.get(
                "OAS_PRE_VALIDATION_HANDLER", None
            )
            self.post_validattion_handler = current_app.config.get(
                "OAS_POST_VALIDATION_HANDLER", None
            )

            self.blueprint_url_prefix = current_app.config.get(
                "OAS_BLUEPRINT_URL_PREFIX", self.blueprint_url_prefix
            )

            self.blueprint_name = current_app.config.get(
                "OAS_BLUEPRINT_NAME", self.blueprint_name
            )

            self.register_blueprint = current_app.config.get(
                "OAS_REGISTER_BLUEPRINT", self.__register_blueprint
            )
            self.register_json_route = current_app.config.get(
                "OAS_REGISTER_JSON_ROUTE", self.__register_json_route
            )

            self.register_ui_route = current_app.config.get(
                "OAS_REGISTER_UI_ROUTE", self.__register_ui_route
            )

            self.spec_json_url = current_app.config.get(
                "OAS_JSON_URL", self.__spec_json_url
            )
            self.json_endpoint = current_app.config.get(
                "OAS_JSON_ENDPOINT", None
            )
            self.ui_endpoint = current_app.config.get("OAS_UI_ENDPOINT", None)
            self.spec_ui_url = current_app.config.get(
                "OAS_UI_URL", self.__spec_ui_url
            )

            self.root_dir = current_app.config.get(
                "OAS_ROOT_DIR", app.root_path
            )

            self.__oas_dirname = current_app.config.get(
                "OAS_DIR", self.__oas_dirname
            )
            self.__fragments_dir = current_app.config.get(
                "FRAGMENTS_DIRNAME", self.__fragments_dir
            )
            self.__cache_dir = current_app.config.get(
                "CACHE_DIRNAME", self.__cache_dir
            )

            self.__oas_sections_file_name = current_app.config.get(
                "DRAFT_FILENAME", self.__oas_sections_file_name
            )
            self.__paths_details_dir = current_app.config.get(
                "PATHS_DETAILS_DIR", self.__paths_details_dir
            )

            self.__final_file_name = current_app.config.get(
                "OAS_FINAL_FILENAME", self.__final_file_name
            )
            self.__override_file_name = current_app.config.get(
                "OAS_OVERRIDE_FILENAME", self.__override_file_name
            )

            self.use_long_stubs = current_app.config.get(
                "OAS_LONG_STUB", self.__use_long_stubs
            )
            self.spec_files_locator = current_app.config.get(
                "OAS_SPEC_FILES_LOCATOR", self.__spec_files_locator
            )

            self.excluded_methods = current_app.config.get(
                "OAS_EXCLUDED_METHODS", self.__excluded_methods
            )
            self.allowed_methods = [
                method
                for method in current_app.config.get(
                    "OAS_ALLOWED_METHODS", self.__allowed_methods
                )
                if method not in self.excluded_methods
            ]
            self.ui_config_url = current_app.config.get(
                "OAS_UI_CONFIG_URL", self.__ui_config_url
            )

        self.oas_dir = os.path.join(self.root_dir, self.__oas_dirname)
        self.fragments_dir = os.path.join(self.oas_dir, self.__fragments_dir)

        self.cache_dir = os.path.join(self.oas_dir, self.__cache_dir)
        self.paths_details_dir = os.path.join(
            self.fragments_dir, self.__paths_details_dir
        )

        self.override_file = os.path.join(
            self.oas_dir, self.__override_file_name
        )
        self.final_file = os.path.join(self.oas_dir, self.__final_file_name)
        self.oas_sections_file = os.path.join(
            self.fragments_dir, self.__oas_sections_file_name
        )
        self.sections_files_list = [
            self.oas_sections_file,
            self.override_file,
        ]
