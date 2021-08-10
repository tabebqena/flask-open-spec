from copy import deepcopy
from typing import Dict, TYPE_CHECKING

from ._parameters import get_app_paths
from ._utils import load_file, merge_recursive
from .builder import OasBuilder

if TYPE_CHECKING:
    from ._editor import TemplatesEditor
    from .oas_config import OasConfig


def __load_data(config: "OasConfig", editor: "TemplatesEditor"):
    sections_data = load_file(config.oas_sections_file)
    overrides = load_file(config.override_file)
    snippet_files_data = editor.load_snippet_files()
    #
    builder_data = OasBuilder.data
    builder_data = _parse_star_method(config, builder_data)
    data = merge_recursive(
        [
            overrides,
            builder_data,
            snippet_files_data,
            sections_data,
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
