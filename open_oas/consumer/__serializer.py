from functools import lru_cache, wraps
from http import HTTPStatus
from logging import warning

from marshmallow import Schema
from ..plugin.utils import resolve_schema_instance
from typing import Union, Any, TYPE_CHECKING, cast
from flask import request
from ._utils import (
    _resolve_oas_object,
    _parse_headers,
    _parse_status,
    _get_best_response,
    _get_best_media_type_object,
    _get_row_oas,
    _parse_view_function_res,
    _get_accepts_headers,
)

if TYPE_CHECKING:
    from ..open_oas import OpenOas

from .._parameters import rule_to_path

from werkzeug.datastructures import Headers
from werkzeug.wrappers import Response as BaseResponse


class __ResponseSerializer:
    def __init__(self, open_oas: "OpenOas") -> None:
        self.open_oas = open_oas
        self.app = open_oas.app
        self.config = open_oas.config
        if self.config.serialize_response:
            self.app.before_first_request(self.wrap_all_functions)

        else:
            return
        self.default_mime_type = self.config.default_response_mime_type
        self.app = open_oas.app
        self.row_oas = {}
        self.final_oas = {}

    def wrap_all_functions(self):
        old_view_functions = {}
        for e, v in self.app.view_functions.items():
            old_view_functions[e] = v
        for endpoint in self.app.view_functions.keys():
            func = old_view_functions[request.endpoint]

            @wraps(func)
            def wrapped(*args, **kwargs):
                func_res = func(*args, **kwargs)
                try:
                    return self.__serialize_response(func_res)
                except Exception as e:
                    warning(e)
                    return func_res

            self.app.view_functions[endpoint] = wrapped

    @lru_cache(maxsize=50)
    def __get_response_schema(
        self,
        status: HTTPStatus,
        mimetype=str,
        accepts: str = "",
    ):
        row_oas = _get_row_oas(self)
        responses = (
            row_oas.get("paths", {})
            .get(rule_to_path(request.url_rule), {})
            .get(request.method.lower(), {})
            .get("responses", {})
        )
        response_object = _get_best_response(responses, status)
        response_object = _resolve_oas_object(
            row_oas, response_object, "response"
        )

        media_type_object = _get_best_media_type_object(
            response_object, mimetype, accepts
        )

        # get x-schema
        xschema = media_type_object.get("x-schema", None)
        if not xschema:
            schema = media_type_object.get("schema", None)
            if schema:
                schema = _resolve_oas_object(row_oas, schema, "schema")
                xschema = cast(Schema, schema.get("x-schema"))
        # schema = resolve_schema(row_oas, schema)
        return xschema

    def __serialize_response(self, rv: Any):
        try:
            rv, status, headers, mimetype = _parse_view_function_res(
                rv, self.app.response_class, self.default_mime_type
            )
        except TypeError:
            return rv

        accepts: str = _get_accepts_headers()
        xschema = self.__get_response_schema(status, mimetype, accepts)

        if xschema:
            instance = resolve_schema_instance(xschema)
            if instance:

                return instance.dump(rv), status, headers

        return rv, status, headers


_OpenOas__ResponseSerializer = __ResponseSerializer
