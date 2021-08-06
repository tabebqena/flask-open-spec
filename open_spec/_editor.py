from .oas_config import OasConfig
from ._parameters import (
    extract_path_parameters,
    get_app_paths,
    preserve_user_edits,
)
import os

from ._constants import (
    EXTERNALDOCS_STUB,
    INFO_STUB,
    SECURITY_SCHEMAS_STUB,
    TAGS_STUB,
    REQUEST_SCHEMAS_INTRO,
    REQUEST_STUB,
    RESPONSE_MAPPING_INTRO,
    RESPONSE_STUB,
    SERVERS_STUB,
    PATHS_ITEM_STUB,
    OPERATION_STUB,
)
from ._utils import (
    load_file,
    merge_recursive,
    yaml_dump,
)


class Editor:
    def __init__(self, config: OasConfig) -> None:
        self.config = config

    def upadte_draft_file(self):
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

    def extract_paths_details(self, document_options=False):
        data = {}
        app_paths = get_app_paths()
        prev = load_file(self.config.paths_file, {})
        for path in app_paths:
            path_data = merge_recursive(
                [prev.get("paths", {}).get(path, {}), PATHS_ITEM_STUB]
            )
            methods = app_paths[path]
            for method in methods:
                if method.lower() in ["get", "delete", "head"]:
                    continue
                if method.lower() == "options" and not document_options:
                    continue
                path_data[method] = merge_recursive(
                    [
                        prev.get("paths", {}).get(path, {}).get(method, {}),
                        OPERATION_STUB,
                    ]
                )
                # data.setdefault("paths", {}).setdefault(path, {}).setdefault(
                #    method,
                #    merge_recursive(
                #        [
                #            prev.get("paths", {}).get(path, {}).get(method, {}),
                #            OPERATION_STUB,
                #        ]
                #    ),
                # )
            data.setdefault("paths", {}).setdefault(path, path_data)
        return data

    def upadte_paths_details_file(self, document_options=False):
        data = self.extract_paths_details(document_options)
        yaml_dump("", data, self.config.paths_file)

    def update_path_parameters(self, document_options=False):
        data: dict = extract_path_parameters(document_options=document_options)
        file_path = self.config.parameters_file
        previous = load_file(file_path, {})
        data = preserve_user_edits(data, previous)
        yaml_dump("", data, file_path)

    def extract_request_bodies(self, document_options=False):
        data = {}
        app_paths = get_app_paths()
        for path in app_paths:
            methods = app_paths[path]
            for method in methods:
                if method.lower() in ["get", "delete", "head"]:
                    continue
                if method.lower() == "options" and not document_options:
                    continue
                data.setdefault("paths", {}).setdefault(path, {}).setdefault(
                    method, {}
                ).setdefault("requestBody", REQUEST_STUB)
        return data

    def update_request_file(self, document_options=False):
        file_path = self.config.request_body_file

        previous_data = load_file(file_path, {})
        data = self.extract_request_bodies(document_options=document_options)

        data = merge_recursive([data, previous_data])
        yaml_dump(REQUEST_SCHEMAS_INTRO, data, file_path)

    def extract_responses(self, document_options=False):
        data = {}
        app_paths = get_app_paths()

        for path in app_paths:
            methods = app_paths[path]
            for method in methods:
                if method.lower() == "options" and not document_options:
                    continue
                data.setdefault("paths", {}).setdefault(path, {}).setdefault(
                    method, {}
                ).setdefault("responses", RESPONSE_STUB)
        return data

    def update_responses_file(self, document_options=False):
        data = self.extract_responses(document_options=document_options)
        file_path = self.config.responses_file

        previous_data = load_file(file_path, {})
        data = merge_recursive([data, previous_data])
        yaml_dump(RESPONSE_MAPPING_INTRO, data, file_path)
