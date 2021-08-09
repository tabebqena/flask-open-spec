from copy import deepcopy
from typing import Dict, TYPE_CHECKING

from ._parameters import (
    extract_path_parameters,
    get_app_paths,
    VALID_METHODS_OPENAPI_V3,
)
from ._utils import load_file, merge_recursive
from .builder import OasBuilder

if TYPE_CHECKING:
    from ._editor import TemplatesEditor
    from .oas_config import OasConfig
    from .open_spec import OpenSpec


def _load_or_fetch(save_files, file_path, fetcher, fetcher_kwargs={}):
    if save_files:
        return load_file(file_path)
    return fetcher(**fetcher_kwargs)


def __load_data(config: "OasConfig", editor: "TemplatesEditor"):
    draft_data = load_file(config.draft_file)
    paths_details = _load_or_fetch(
        config.save_files,
        config.paths_file,
        editor.extract_paths_details,
    )
    parameters = _load_or_fetch(
        config.save_files,
        config.parameters_file,
        extract_path_parameters,
        {
            "long_stub": config.use_long_stubs,
            "allowed_methods": config.allowed_methods,
        },
    )
    requestBodies = _load_or_fetch(
        config.save_files,
        config.request_body_file,
        editor.extract_request_bodies,
    )

    responses = _load_or_fetch(
        config.save_files,
        config.responses_file,
        editor.extract_responses,
    )
    overrides = load_file(config.override_file)
    snippet_files_data = editor.load_snippet_files()
    #
    builder_data = _parse_star_method(config, OasBuilder.data)
    data = merge_recursive(
        [
            overrides,
            builder_data,
            snippet_files_data,
            paths_details,
            parameters,
            requestBodies,
            responses,
            draft_data,
        ]
    )
    data = _clean_invalid_paths(data)
    data = _clean_invalid_request_bodies(data)

    return data


def _clean_invalid_paths(data):
    app_paths_list = get_app_paths()
    data_paths = deepcopy(data.get("paths", {}))
    keys = data.get("paths", {}).keys()
    for path in keys:
        if path not in app_paths_list:
            del data_paths[path]
    data["paths"] = data_paths
    return data


def _parse_star_method(config: "OasConfig", data: Dict[str, Dict]):
    app_allowed_methods = config.allowed_methods
    app_paths_list = get_app_paths()
    data_paths = deepcopy(data.get("paths", {}))
    for path in data_paths:
        path_value = data_paths[path]
        keys = path_value.keys()
        if "*" in keys:
            allowed_methods = [
                method
                for method in app_paths_list.get(path, [])
                if method in app_allowed_methods
            ]

            for method in allowed_methods:
                if method in keys:
                    continue
                data_paths[path][method] = data_paths[path]["*"]
            del data_paths[path]["*"]
    data["paths"] = data_paths
    return data


def _clean_invalid_request_bodies(data: Dict[str, Dict[str, Dict]]):
    paths = data.get("paths", {})
    for path, path_obj in paths.items():
        for method in ["get", "delete", "head"]:
            if path_obj.get(method, {}).get("requestBody", None):
                del paths[path][method]["requestBody"]
    data["paths"] = paths
    return data


_OpenSpec__load_data = __load_data
