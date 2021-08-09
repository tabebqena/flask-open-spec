from flask import current_app
from .oas_config import OasConfig
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
    def __init__(self, open_spec: "OpenSpec") -> None:
        self.open_spec = open_spec
        self.config = open_spec.config
        self.app_paths = self.open_spec._app_paths

        self.path_details = {}
        self.parameters = {}
        self.request_bodies = {}

        self.responses = {}

    def update_draft_file(self):
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
        if os.path.exists(self.config.draft_file):
            prev = load_file(self.config.draft_file, None)
            if prev:
                data = merge_recursive([prev, data])
        yaml_dump("", data, self.config.draft_file)

    def extract_paths_details(self):
        data = {}
        prev = load_file(self.config.paths_file, {})
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

        for path in self.app_paths:
            path_data = cast(
                dict,
                merge_recursive(
                    [prev.get("paths", {}).get(path, {}), path_stub]
                ),
            )
            methods = self.app_paths[path]
            for method in methods:
                """if method.lower() in ["get", "delete", "head"]:
                continue
                """
                if method.lower() not in self.config.allowed_methods:
                    continue
                path_data[method] = merge_recursive(
                    [
                        prev.get("paths", {}).get(path, {}).get(method, {}),
                        operation_stub,
                    ]
                )
            data.setdefault("paths", {}).setdefault(path, path_data)
        self.path_details = data
        return data

    def __upadte_paths_details_file(self):
        data = self.extract_paths_details()
        yaml_dump("", data, self.config.paths_file)

    def __update_path_parameters(self):
        data: dict = extract_path_parameters(
            allowed_methods=self.config.allowed_methods,
            long_stub=self.config.use_long_stubs,
        )
        file_path = self.config.parameters_file
        previous = load_file(file_path, {})
        data = preserve_user_edits(
            data,
            previous,
            allowed_methods=self.config.allowed_methods,
        )
        yaml_dump("", data, file_path)
        self.parameters = data

    def extract_request_bodies(self):
        data = {}
        app_paths = self.app_paths
        stub = (
            lambda: REQUEST_STUB_LONG
            if self.config.use_long_stubs
            else REQUEST_STUB_SHORT
        )()
        for path in app_paths:
            methods = app_paths[path]
            for method in methods:
                method = method.lower()
                if (
                    method in ["get", "delete", "head"]
                    or method not in self.config.allowed_methods
                ):
                    continue
                data.setdefault("paths", {}).setdefault(path, {}).setdefault(
                    method.lower(), {}
                ).setdefault("requestBody", stub)
        self.request_bodies = data
        return data

    def __update_request_file(self):
        file_path = self.config.request_body_file

        previous_data = load_file(file_path, {})
        data = self.extract_request_bodies()

        data = merge_recursive([data, previous_data])
        yaml_dump("", data, file_path)

    def extract_responses(self):
        data = {}
        app_paths = self.app_paths
        stub = (
            lambda: RESPONSE_STUB_LONG
            if self.config.use_long_stubs
            else RESPONSE_STUB_SHORT
        )()
        for path in app_paths:
            methods = app_paths[path]
            for method in methods:
                if method.lower() not in self.config.allowed_methods:
                    continue
                data.setdefault("paths", {}).setdefault(path, {}).setdefault(
                    method, {}
                ).setdefault("responses", stub)
        self.responses = data
        return data

    def __update_responses_file(self):
        data = self.extract_responses()
        file_path = self.config.responses_file

        previous_data = load_file(file_path, {})
        data = merge_recursive([data, previous_data])
        yaml_dump("", data, file_path)

    def __call_spec_files_locator_func(self, kwargs) -> List:
        if not self.config.spec_files_locator:
            return [None, None, None]
        res = self.config.spec_files_locator(**kwargs)
        res_ = [None, None, False]
        if type(res) == tuple:
            res_[0] = res[0] or None
            res_[1] = res[1] or kwargs["path"]
            res_[2] = res[2] or False
        else:
            res_[0] = res
            res_[1] = kwargs["path"]
            res_[2] = False
        return res_

    def update_snippets_files(self, data={}):
        if not self.config.spec_files_locator:
            return
        if data:
            rules: List[Rule] = current_app.url_map._rules
            kwargs = {}
            for r in rules:
                kwargs["rule"] = r
                kwargs["path"] = rule_to_path(r)
                if self.config.spec_files_locator:
                    (
                        file_path,
                        key,
                        editable,
                    ) = self.__call_spec_files_locator_func(kwargs)

                    if file_path:
                        if editable or not os.path.exists(file_path):
                            _data = merge_recursive(
                                [
                                    {
                                        "paths": {
                                            kwargs["path"]: data.get(
                                                "paths", {}
                                            ).get(kwargs["path"])
                                        }
                                    },
                                    load_file(file_path, {}),
                                ]
                            )
                            yaml_dump("", _data, file_path)
        else:
            details = self.extract_paths_details()
            parameters = extract_path_parameters(
                long_stub=self.config.use_long_stubs,
                allowed_methods=self.config.allowed_methods,
            )
            requests = self.extract_request_bodies()
            responses = self.extract_responses()

            rules: List[Rule] = current_app.url_map._rules
            kwargs = {}
            for r in rules:
                kwargs["rule"] = r
                kwargs["path"] = rule_to_path(r)
                if self.config.spec_files_locator:
                    (
                        file_path,
                        key,
                        editable,
                    ) = self.__call_spec_files_locator_func(kwargs)

                    if file_path:
                        if editable or not os.path.exists(file_path):
                            _data = {}
                            # if not data:
                            _data = merge_recursive(
                                [
                                    load_file(file_path, {}),
                                    {
                                        "paths": {
                                            key: details.get("paths", {}).get(
                                                kwargs["path"]
                                            )
                                        }
                                    },
                                    {
                                        "paths": {
                                            key: parameters.get(
                                                "paths", {}
                                            ).get(kwargs["path"])
                                        }
                                    },
                                    {
                                        "paths": {
                                            key: requests.get("paths", {}).get(
                                                kwargs["path"]
                                            )
                                        }
                                    },
                                    {
                                        "paths": {
                                            key: responses.get("paths", {}).get(
                                                kwargs["path"]
                                            )
                                        }
                                    },
                                ]
                            )
                            """else:
                                _data = merge_recursive(
                                    [
                                        load_file(file_path, {}),
                                        {
                                            "paths": {
                                                kwargs["path"]: data.get(
                                                    "paths", {}
                                                ).get(kwargs["path"])
                                            }
                                        },
                                    ]
                                )"""
                            # print(256, _data)
                            yaml_dump("", _data, file_path)

    def load_snippet_files(self):
        if not self.config.spec_files_locator:
            return {}
        rules: List[Rule] = current_app.url_map._rules
        kwargs = {}
        data = {}
        for r in rules:
            kwargs["rule"] = r
            kwargs["path"] = rule_to_path(r)
            if self.config.spec_files_locator:
                file_path, key, editable = self.__call_spec_files_locator_func(
                    kwargs
                )
                if file_path:
                    file_data = load_file(file_path, {})

                    data = merge_recursive(
                        [
                            data,
                            {
                                "paths": {
                                    kwargs["path"]: file_data.get(
                                        "paths", {}
                                    ).get(key, {})
                                }
                            },
                        ]
                    )
        return data

    def _update_all(self):
        self.update_draft_file()
        self.__upadte_paths_details_file()
        self.__update_path_parameters()
        self.__update_request_file()
        self.__update_responses_file()
