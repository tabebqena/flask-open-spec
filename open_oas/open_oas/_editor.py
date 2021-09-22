from copy import deepcopy
from .oas_config import OasConfig
import click
from flask import current_app
from ._parameters import (
    extract_path_parameters,
    preserve_user_edits,
)
import os
from typing import Dict, List, cast
from ._parameters import rule_to_path
from ._constants import (
    EXTERNALDOCS_STUB,
    INFO_STUB,
    SECURITY_SCHEMAS_STUB,
    TAGS_STUB,
    REQUEST_STUB_LONG,
    REQUEST_STUB_SHORT,
    RESPONSE_STUB_LONG,
    RESPONSE_STUB_SHORT,
    SERVERS_STUB,
    PATHS_ITEM_STUB_LONG,
    PATHS_ITEM_STUB_SHORT,
    OPERATION_STUB_LONG,
    OPERATION_STUB_SHORT,
)
from werkzeug.routing import Rule
from ._utils import (
    load_file,
    merge_recursive,
    yaml_dump,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .open_oas import OpenSpec


#


def make_template_data(config: "OasConfig", app_paths: Dict[str, List[str]]):
    INFO_STUB["title"] = config.title
    INFO_STUB["version"] = config.version
    data = {
        "openapi": "3.0.2",
        "info": INFO_STUB,
        "servers": SERVERS_STUB,
        "tags": TAGS_STUB,
        "components": {"securitySchemes": SECURITY_SCHEMAS_STUB, "schemas": {}},
        "externalDocs": EXTERNALDOCS_STUB,
    }
    #
    paths_details = {}
    #
    path_stub = (
        lambda: PATHS_ITEM_STUB_LONG
        if config.use_long_stubs
        else PATHS_ITEM_STUB_SHORT
    )()
    operation_stub = (
        lambda: OPERATION_STUB_LONG
        if config.use_long_stubs
        else OPERATION_STUB_SHORT
    )()
    request_stub = (
        lambda: REQUEST_STUB_LONG
        if config.use_long_stubs
        else REQUEST_STUB_SHORT
    )()

    response_stub = (
        lambda: RESPONSE_STUB_LONG
        if config.use_long_stubs
        else RESPONSE_STUB_SHORT
    )()
    #
    for path in app_paths:
        path_data = cast(dict, deepcopy(path_stub))
        methods = app_paths[path]
        for method in methods:
            if method.lower() not in config.allowed_methods:
                continue
            path_data[method] = deepcopy(operation_stub)
            if method not in ["get", "delete", "head"]:
                path_data[method]["requestBody"] = deepcopy(request_stub)
            path_data[method]["responses"] = deepcopy(response_stub)
        paths_details[path] = path_data
    #
    parameters: dict = extract_path_parameters(
        allowed_methods=config.allowed_methods,
        long_stub=config.use_long_stubs,
    )
    #
    template_data = cast(
        dict, merge_recursive([{"paths": paths_details}, parameters, data])
    )
    return template_data


#
class TemplatesEditor:
    def __init__(
        self, open_oas: "OpenSpec", template_data: Dict, echo=False
    ) -> None:
        self.open_oas = open_oas
        self.config = open_oas.config
        self.app_paths = self.open_oas._app_paths
        self.template_data: dict = template_data
        self.__mk_dirs_files()
        self.__update_all()
        self.echo(echo)

    def __update_all(self):
        self.__sync_sections_file()
        self.__sync_paths_details_file()
        self.__sync_components_file()

    def __mk_dirs_files(self):
        try:
            os.makedirs(self.config.oas_dir_path)
        except Exception as e:
            pass
        try:
            os.makedirs(self.config.fragments_dir_path)
            os.makedirs(self.config.paths_dir_path)
            os.makedirs(self.config.overrides_dir_path)
        except Exception as e:
            pass
        if self.config.save_sections_files:
            for f in self.config.sections_files_list:
                if not os.path.exists(f):
                    with open(f, "w") as f_:
                        f_.close()
        else:
            if not os.path.exists(self.config.overrides_dir_path):
                open(self.config.overrides_dir_path, "w").close()

    def echo(self, echo=True):
        if not echo and self.config.debug:
            return
        if self.config.save_sections_files:
            click.echo(
                "Now, It is your time to edit the generated files:\
                        \n - {0}\n - {1}\n ".format(  # - {2}\n - {3}\n - {4}\n
                    self.config.sections_file_path,
                    # self.config.request_body_file,
                    # self.config.responses_file,
                    self.config.overrides_dir_path,
                )
            )
        else:
            click.echo(
                "- generated files:\
                        \n - {0}\n - {1}\n ".format(
                    self.config.sections_file_path,
                    self.config.overrides_dir_path,
                )
            )

    def __sync_sections_file(self):
        data = cast(dict, deepcopy(self.template_data))
        data = {
            k: v
            for k, v in data.items()
            if k in ["openapi", "tags", "externalDocs", "servers", "info"]
        }
        prev = load_file(self.config.sections_file_path, {})
        data = merge_recursive([prev, data])
        if self.config.save_sections_files:
            yaml_dump("", data, self.config.sections_file_path)
        self.template_data = cast(
            dict, merge_recursive([data, self.template_data])
        )

    def __sync_components_file(self):
        data = cast(dict, deepcopy(self.template_data))

        prev = load_file(
            self.config.components_file_path,
            {},
        )
        data = cast(dict, merge_recursive([prev, data]))
        yaml_dump(
            "",
            {"components": data.get("components", {})},
            self.config.sections_file_path,
        )
        self.template_data = cast(
            dict, merge_recursive([data, self.template_data])
        )

    def __sync_paths_details_file(self):
        rules = current_app.url_map._rules
        for rule in rules:
            path = rule_to_path(rule)

            file_path = self.__locate_oas_file(rule)
            prev = load_file(file_path, {})
            user_edited_parameters = preserve_user_edits(
                {
                    "paths": {
                        path: self.template_data.get("paths", {}).get(path, {})
                    }
                },
                prev,
                self.config.allowed_methods,
            )
            path_data = merge_recursive(
                [
                    prev,
                    user_edited_parameters,
                    {
                        "paths": {
                            path: self.template_data.get("paths", {}).get(
                                path, {}
                            )
                        }
                    },
                ]
            )
            try:
                os.makedirs(os.path.dirname(file_path))
            except:
                pass

            yaml_dump("", path_data, file_path)
            self.template_data = cast(
                dict,
                merge_recursive(
                    [
                        {
                            "paths": {
                                path: path_data,
                            }
                        },
                        self.template_data,
                    ]
                ),
            )

    def __locate_oas_file(self, rule: Rule) -> str:
        path = rule_to_path(rule)
        file_path = None
        if self.config.oas_files_locator:
            file_path = self.config.oas_files_locator(rule=rule, path=path)

        if not file_path:
            path_ = path.replace("/", ".") + ".yaml"
            file_path = os.path.join(self.config.paths_dir_path, path_)
        return file_path

    def load_snippet_files(self):
        data = {}
        rules = current_app.url_map._rules
        for rule in rules:
            data = merge_recursive(
                [data, load_file(self.__locate_oas_file(rule), {})]
            )
        return data
