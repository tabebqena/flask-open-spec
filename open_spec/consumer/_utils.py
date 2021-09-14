from http import HTTPStatus
from typing import Literal, Union
from werkzeug.datastructures import Headers


def resolve_oas_object(
    oas_data: dict,
    obj: dict,
    type_: Literal[
        "schema",
        "rb",
        "response",
    ] = None,
):
    if not type_:
        raise RuntimeError("Type should specified")
    if not obj or not isinstance(obj, dict):
        return obj

    ref = obj.get("$ref", None)

    if ref:
        _map = {
            "schema": "schemas",
            "rb": "requestBodies",
            "response": "responses",
        }
        rv = ref.split(f"#/components/{_map[type_]}/")[-1]
        obj = oas_data.get("components", {}).get(_map[type_], {}).get(rv, {})
        return obj
    return obj


def parse_headers(headers: Union[dict, list, tuple, Headers]) -> Headers:
    """
    ``headers`` is Header or a dictionary or a list of ``(key, value)``
    tuples.
    or ?? tuple of tuples
    """
    if isinstance(headers, Headers):
        return headers
    rv = Headers()
    items: tuple = ()

    if isinstance(headers, dict):
        items = tuple(headers.items())
    if isinstance(headers, tuple):
        items = headers
    if isinstance(headers, list):
        items = tuple(headers)
    for item in items:
        rv.add(item[0], item[1])
    return rv


def parse_status(status: Union[None, int, HTTPStatus] = None) -> HTTPStatus:
    if isinstance(status, HTTPStatus):
        return status
    if not status:
        return HTTPStatus.OK
    if isinstance(status, int):
        return HTTPStatus(status)
    return status
