from copy import deepcopy
import os
from .builder import OasBuilder
from typing import Any, Dict, TYPE_CHECKING, cast

from ._parameters import get_app_paths
from ._utils import load_file, merge_recursive

if TYPE_CHECKING:
    from .oas_config import OasConfig
    from .open_oas import OpenOas


def __load_overrides(open_oas: "OpenOas") -> dict:
    data = {}
    dir = open_oas.config.overrides_dir_path
    if not os.path.exists(dir):
        return data
    files = os.listdir(dir)
    files.sort()
    for f in files:
        p = os.path.join(dir, f)
        with open(p, "r") as f:
            data = cast(dict, merge_recursive([load_file(f), data]))

    return data


def __load_data(
    open_oas: "OpenOas",
    templates_data: Dict[str, Any],
    input_oas_data: dict = {},
):
    config = open_oas.config
    # editor = open_oas._editor

    # sections_data = load_file(config.sections_file)
    # components_data = load_file(config.components_file)
    overrides = __load_overrides(open_oas)
    # snippet_files_data = editor.load_snippet_files()
    #
    data = cast(
        dict,
        merge_recursive(
            [
                input_oas_data,
                templates_data,
                # sections_data,
                # components_data,
                # snippet_files_data,
                overrides,
            ]
        ),
    )  # type: ignore
    builder = OasBuilder(
        data,
        allowed_methods=config.allowed_methods,
    )
    builder_data = builder.get_data()
    builder_data = _parse_star_method(config, builder_data)
    data = merge_recursive(
        [
            overrides,
            builder_data,
            # snippet_files_data,
            # sections_data,
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


_OpenOas__load_data = __load_data
