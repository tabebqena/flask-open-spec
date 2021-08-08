from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from ._parameters import get_app_paths
from ._utils import clean_parameters_list, remove_none, remove_empty, clean_data
from ._constants import RESPONSE_STUB_SHORT, RESPONSE_STUB_LONG
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from .oas_config import OasConfig


def get_valid_responses(responses: Dict[str, Dict]):
    responses = remove_none(responses)
    if not responses:
        return RESPONSE_STUB_LONG
    return responses


def _add_paths_to_spec(spec: APISpec, data):
    app_paths_list = get_app_paths()
    no_request_body_methods = ["get", "head"]

    for path in app_paths_list:
        for method in app_paths_list[path]:

            summary: str = data.get("paths", {}).get(path, {}).get("summary")
            description: str = (
                data.get("paths", {}).get(path, {}).get("description")
            )
            parameters = clean_parameters_list(
                data.get("paths", {}).get(path, {}).get("parameters", [])
            )
            operation = (
                data.get("paths", {}).get(path, {}).get(method, {}) or {}
            )
            if operation:
                operation["responses"] = get_valid_responses(
                    operation.get("responses", {})
                )

            if operation and operation.get("requestBody", {}):
                operation["requestBody"] = remove_none(
                    operation.get("requestBody", {})
                )
            if operation and operation.get("parameters", {}):
                operation["parameters"] = clean_parameters_list(
                    operation.get("parameters", [])
                )
            spec.path(
                path,
                summary=summary,
                description=description,
                parameters=parameters,
                operations={method: operation},
            )


def _get_spec_dict(
    data: dict,
    config: "OasConfig",
):
    spec = spec = APISpec(
        title=data.get("info", {}).get("title", config.title),
        version=data.get("info", {}).get("version", config.version),
        openapi_version="3.0.2",
        info=data.get("info", {}),
        plugins=[MarshmallowPlugin()],
    )

    _add_paths_to_spec(spec, data)

    return spec.to_dict()
