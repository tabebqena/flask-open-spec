from copy import deepcopy
from open_spec.builder import OasBuilder
from ._parameters import get_app_paths, extract_path_parameters

from ._utils import load_file, merge_recursive

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .open_spec import OpenSpec
    from .oas_config import OasConfig


def _load_or_fetch(save_files, file_path, fetcher, fetcher_kwargs={}):
    if save_files:
        return load_file(file_path)
    return fetcher(**fetcher_kwargs)


def __load_data(open_spec: "OpenSpec"):
    config = open_spec.config
    draft_data = load_file(config.draft_file)
    paths_details = _load_or_fetch(
        config.save_files,
        config.paths_file,
        open_spec.__editor.extract_paths_details,
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
        open_spec.__editor.extract_request_bodies,
    )

    responses = _load_or_fetch(
        config.save_files,
        config.responses_file,
        open_spec.__editor.extract_responses,
    )
    overrides = load_file(config.override_file)
    spec_files_data = open_spec.__editor.load_snippet_files()
    #
    data = merge_recursive(
        [
            overrides,
            # decorators_data,
            OasBuilder.data,
            spec_files_data,
            paths_details,
            parameters,
            requestBodies,
            responses,
            draft_data,
        ]
    )
    data = _clean_invalid_paths(data)
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
