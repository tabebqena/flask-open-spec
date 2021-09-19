from http import HTTPStatus
from typing import List, Literal, Type, Union
from flask import Flask, request
from werkzeug.datastructures import Headers

from werkzeug.wrappers import Response as BaseResponse


def _resolve_oas_object(
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


def _parse_headers(headers: Union[dict, list, tuple, Headers]) -> Headers:
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


def _parse_status(status: Union[None, int, HTTPStatus] = None) -> HTTPStatus:
    if isinstance(status, HTTPStatus):
        return status
    if not status:
        return HTTPStatus.OK
    if isinstance(status, int):
        return HTTPStatus(status)
    return status


def _get_best_response(responses: dict, status: HTTPStatus):

    response_object = responses.get(int(status), None)
    if not response_object:
        response_object = responses.get(str(int(status)), None)
    # getrange response 2XX 3XX 4XX 5XX
    if not response_object:
        codexx = str(int(status))[0] + "XX"
        response_object = responses.get(codexx, None)
        if not response_object:
            response_object = responses.get(codexx.lower(), None)

    if not response_object:
        response_object = responses.get("default", None)
    return response_object


def _get_mimetype(content_keys: list, accepts: str) -> str:

    accepted_list = accepts.split(",")
    for accept in accepted_list:
        accept = accept.strip()
        if accept.strip() in content_keys:
            return accept
        if accept.endswith("/*"):
            # mt = f"""{accept.split("/")[0]}/*"""
            # print(mt)
            for k in content_keys:
                if k.split("/")[0] == accept.split("/")[0]:
                    return k
    return ""


def _get_best_media_type_object(
    response_object: dict, mimetype: str, accepts: str = ""
):
    if mimetype is None:
        mimetype = ""
    if accepts is None:
        accepts = ""
    # response object is dictionary of description, content
    content = response_object.get("content", {})
    # content is dictionary of mimetype to schema
    content_keys = list(content.keys())
    if not content_keys:
        return None
    media_type_object = content.get(mimetype, {})

    if not media_type_object:
        mt = f"""{mimetype.split("/")[0]}/*"""
        media_type_object = content.get(mt, {})

    if not media_type_object:
        mimetype = _get_mimetype(content_keys, accepts)
        if mimetype:
            media_type_object = content.get(mimetype, {})
    if not media_type_object:
        media_type_object = content.get(content_keys[0], {})
    return media_type_object


def _get_row_oas(obj):
    if obj.row_oas:
        return obj.row_oas
    else:
        obj.row_oas = obj.open_spec.oas_data
    return obj.row_oas


def _parse_view_function_res(rv, response_class: Type, default_mime_type: str):

    if (
        not rv
        or isinstance(rv, response_class)
        or isinstance(rv, BaseResponse)
        or callable(rv)
    ):
        # if the user construct his werzeug.Response or callable, let flask to handle
        raise TypeError
    status = None
    headers: Union[dict, Headers, list, tuple] = {}

    # unpack tuple returns
    if isinstance(rv, tuple):
        len_rv = len(rv)

        # a 3-tuple is unpacked directly
        if len_rv == 3:
            rv, status, headers = rv
        # decide if a 2-tuple has status or headers
        elif len_rv == 2:
            if isinstance(rv[1], (Headers, dict, tuple, list)):
                rv, headers = rv
            else:
                rv, status = rv
        # other sized tuples are not allowed
        else:
            raise TypeError(
                "The view function did not return a valid response tuple."
                " The tuple must have the form (body, status, headers),"
                " (body, status), or (body, headers)."
            )

    headers = _parse_headers(headers)
    status = _parse_status(status)
    mimetype: str = headers.get("Content-Type", "").split(";")[0].strip()
    if not mimetype:
        mimetype = default_mime_type
    return rv, status, headers, mimetype


def _get_request_body_data(include_args=False):
    if request.is_json:
        return request.get_json()

    mt = request.mimetype
    if mt in [
        "application/x-www-form-urlencoded",
    ]:
        if include_args:
            return request.values.to_dict()
        else:
            return request.form.to_dict()
    elif mt in ["multipart/form-data"]:
        return request.files.to_dict()
    elif include_args and request.args:
        return request.args.to_dict()

    return request.data or {}
