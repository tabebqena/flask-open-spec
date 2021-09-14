from functools import lru_cache, wraps
from http import HTTPStatus
from logging import warning

from marshmallow import Schema
from ..plugin.utils import resolve_schema_instance
from typing import Union, Any, TYPE_CHECKING, cast
from flask import request
from ._utils import (
    resolve_oas_object,
    parse_headers,
    parse_status,
)

if TYPE_CHECKING:
    from ..open_spec import OpenSpec

from .._parameters import rule_to_path

from werkzeug.datastructures import Headers
from werkzeug.wrappers import Response as BaseResponse


class __ResponseSerializer:
    def __init__(self, open_spec: "OpenSpec") -> None:
        self.open_spec = open_spec
        self.app = open_spec.app
        self.config = open_spec.config
        if self.config.serialize_response:
            self.app.before_first_request(self.wrap_all_functions)

        else:
            return
        self.default_mime_type = self.config.default_response_mime_type
        self.app = open_spec.app
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

    def __get_oas_data(self):
        if self.row_oas:
            return self.row_oas
        else:
            self.row_oas = self.open_spec.oas_data
        return self.row_oas

    @lru_cache(maxsize=50)
    def __get_response_schema(
        self,
        status: Union[HTTPStatus, Any],
        mimetype=str,
        accepts: str = "",
    ):
        row_oas = self.__get_oas_data()
        responses = (
            row_oas.get("paths", {})
            .get(rule_to_path(request.url_rule), {})
            .get(request.method.lower(), {})
            .get("responses", {})
        )
        response_object = responses.get(int(status), None)
        if not response_object:
            response_object = responses.get(str(int(status)), None)
        # getrange response 2XX 3XX 4XX 5XX
        if not response_object:
            codexx = str(status)[0] + "XX"
            response_object = responses.get(codexx, None)
            if not response_object:
                response_object = responses.get(codexx.lower(), None)

        if not response_object:
            response_object = responses.get("default", None)
        if not response_object:
            return None
        response_object = resolve_oas_object(
            row_oas, response_object, "response"
        )
        # response object is dictionary of description, content
        content = response_object.get("content", {})
        # content is dictionary of mimetype to schema
        content_keys = content.keys()
        if not content_keys:
            return None
        media_type_object = content.get(mimetype, {})
        found = []
        if not media_type_object:
            accepted_list = accepts.split(",")
            for accept in accepted_list:
                if accept in content_keys:
                    found.append(accept)
            if not found:
                for accept in accepts:
                    if accept.endswith("/*"):
                        for k in content_keys:
                            if k.split("/")[0] == accept.split("/")[0]:
                                found.append(k)
        if found:
            media_type_object = content.get(found[0], {})
        else:
            media_type_object = content.get(list(content_keys)[0], {})

        # get x-schema

        xschema = media_type_object.get("x-schema", None)

        if not xschema:
            schema = media_type_object.get("schema", None)
            if schema:
                schema = resolve_oas_object(row_oas, schema, "schema")
                xschema = cast(Schema, schema.get("x-schema"))

        # schema = resolve_schema(row_oas, schema)
        return xschema

    def __serialize_response(self, rv: Any):
        if not rv:
            # if none > leave flask to handle it
            return rv
        if isinstance(rv, self.app.response_class):
            # if the user construct his special response, don't interact
            return rv
        if isinstance(rv, BaseResponse) or callable(rv):
            # if the user construct his werzeug.Response or callable, let flask to handle
            return rv
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

        headers = parse_headers(headers)
        status = parse_status(status)

        mimetype: str = headers.get("Content-Type", "").split(";")[0].strip()
        if not mimetype:
            mimetype = self.default_mime_type
        accepts: str = ",".join(
            [
                a.split(";")[0].strip()
                for a in request.headers.get("Accept", "").split(",")
            ]
        )
        xschema = self.__get_response_schema(status, mimetype, accepts)
        if xschema:
            instance = resolve_schema_instance(xschema)
            if instance:
                return instance.dump(rv), status, headers

        return rv, status, headers


_OpenSpec__ResponseSerializer = __ResponseSerializer
