from copy import deepcopy
from distutils.command.config import config
from pprint import pprint
import click
from flask import current_app
from ._parameters import (
    extract_path_parameters,
    preserve_user_edits,
)
import os
from typing import List, cast
from werkzeug.routing import Rule
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
from ._utils import (
    load_file,
    merge_recursive,
    yaml_dump,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .open_spec import OpenSpec

#
#
class TemplatesEditor:
    def __init__(self, open_spec: "OpenSpec", echo=False) -> None:
        self.open_spec = open_spec
        self.config = open_spec.config
        self.app_paths = self.open_spec._app_paths
        self.init(echo)
        self.template_data: dict = {}

    def init(self, echo=True):
        self.make_template_data()
        self.mk_dirs_files()
        self._update_all()
        self.echo(echo)

    def mk_dirs_files(self):
        try:
            os.makedirs(self.config.oas_dir)
        except:
            pass
        try:
            os.makedirs(self.config.fragments_dir)
            os.makedirs(self.config.paths_details_dir)
        except Exception as e:
            pass
        if self.config.save_sections_files:
            for f in self.config.sections_files_list:
                if not os.path.exists(f):
                    open(f, "w").close()
        else:
            if not os.path.exists(self.config.override_file):
                open(self.config.override_file, "w").close()

    def echo(self, echo=True):
        if not echo and self.config.debug:
            return
        if self.config.save_sections_files:
            click.echo(
                "Now, It is your time to edit the generated files:\
                        \n - {0}\n - {1}\n - {2}\n - {3}\n - {4}\n ".format(
                    self.config.oas_sections_file,
                    # self.config.request_body_file,
                    # self.config.responses_file,
                    self.config.override_file,
                )
            )
        else:
            click.echo(
                "- generated files:\
                        \n - {0}\n - {1}\n ".format(
                    self.config.oas_sections_file,
                    self.config.override_file,
                )
            )

    def make_template_data(self):
        INFO_STUB["title"] = self.config.title
        INFO_STUB["version"] = self.config.version
        data = {
            "openapi": "3.0.2",
            "info": INFO_STUB,
            "servers": SERVERS_STUB,
            "tags": TAGS_STUB,
            "components": {"securitySchemes": SECURITY_SCHEMAS_STUB},
            "externalDocs": EXTERNALDOCS_STUB,
        }
        #
        paths_details = {}
        #
        path_stub = (
            lambda: PATHS_ITEM_STUB_LONG
            if self.config.use_long_stubs
            else PATHS_ITEM_STUB_SHORT
        )()
        operation_stub = (
            lambda: OPERATION_STUB_LONG
            if self.config.use_long_stubs
            else OPERATION_STUB_SHORT
        )()
        request_stub = (
            lambda: REQUEST_STUB_LONG
            if self.config.use_long_stubs
            else REQUEST_STUB_SHORT
        )()

        response_stub = (
            lambda: RESPONSE_STUB_LONG
            if self.config.use_long_stubs
            else RESPONSE_STUB_SHORT
        )()
        #
        for path in self.app_paths:
            path_data = cast(dict, deepcopy(path_stub))
            methods = self.app_paths[path]
            for method in methods:
                if method.lower() not in self.config.allowed_methods:
                    continue
                path_data[method] = deepcopy(operation_stub)
                if method not in ["get", "delete", "head"]:
                    path_data[method]["requestBody"] = deepcopy(request_stub)
                path_data[method]["responses"] = deepcopy(response_stub)
            paths_details[path] = path_data
        #
        parameters: dict = extract_path_parameters(
            allowed_methods=self.config.allowed_methods,
            long_stub=self.config.use_long_stubs,
        )
        #
        self.template_data = cast(
            dict, merge_recursive([{"paths": paths_details}, parameters, data])
        )
        yaml_dump("", self.template_data, "res.yaml")

    def _update_all(self):
        self.update_sections_file()
        self.__update_paths_details_file()
        # self.__update_path_parameters()

    def update_sections_file(self):
        data = cast(dict, deepcopy(self.template_data))
        data["paths"] = None
        del data["paths"]

        if os.path.exists(self.config.oas_sections_file):
            prev = load_file(self.config.oas_sections_file, None)
            if prev:
                data = merge_recursive([prev, data])
        yaml_dump("", data, self.config.oas_sections_file)

    def __update_paths_details_file(self):
        rules = current_app.url_map._rules
        for rule in rules:
            path = rule_to_path(rule)
            file_path = None
            if self.config.spec_files_locator:
                file_path = self.__call_spec_files_locator_func(
                    rule=rule, path=path
                )
            if not file_path:
                path_ = path.replace("/", ".") + ".yaml"
                file_path = os.path.join(self.config.paths_details_dir, path_)
            prev = load_file(file_path)
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

    def __call_spec_files_locator_func(self, **kwargs) -> str:
        if not self.config.spec_files_locator:
            return ""
        return self.config.spec_files_locator(**kwargs)

    def load_snippet_files(self):
        data = {}
        rules = current_app.url_map._rules
        for rule in rules:
            path = rule_to_path(rule)
            file_path = None
            if self.config.spec_files_locator:
                file_path = self.__call_spec_files_locator_func(
                    rule=rule, path=path
                )
            if not file_path:
                path_ = path.replace("/", ".") + ".yaml"
                file_path = os.path.join(self.config.paths_details_dir, path_)
            file_data = load_file(file_path, {})
            data = merge_recursive([data, file_data])
        return data
