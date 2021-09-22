from functools import lru_cache
from http import HTTPStatus
import json
from logging import warning

from pyrsistent import b
from ..plugin.utils import resolve_schema_instance
from typing import TYPE_CHECKING, Optional, cast
from flask import abort, g, jsonify, make_response, request
from flask.wrappers import Response
from marshmallow import Schema

if TYPE_CHECKING:
    from ..open_oas import OpenSpec

from .._parameters import rule_to_path
from ._utils import (
    _resolve_oas_object,
    _get_row_oas,
    _get_request_body_data,
)


class __RequestsValidator:
    def __init__(self, open_oas: "OpenSpec") -> None:
        self.open_oas = open_oas
        self.config = open_oas.config
        if self.config.validate_requests:
            open_oas.app.before_request(self.__validate_request_body)
        else:
            return
        self.row_oas = {}

    # should have all keys to used as key for caching
    @lru_cache(maxsize=50)
    def __get_request_body_xschema(self, path: str, method: str, mimetype: str):
        row_oas = _get_row_oas(self)

        if method in ["get", "delete", "head"]:
            return None, False
        body = _resolve_oas_object(
            row_oas,
            (
                row_oas.get("paths", {})
                .get(path, {})
                .get(method.lower(), {})
                .get("requestBody", {})
            ),
            "rb",
        )

        if not body:
            return None, False
        is_required = body.get("required", False)

        xschema = ""
        body_content = body.get("content", {})
        media_type_obj = {}

        media_type_obj = body_content.get(mimetype, {})
        if not media_type_obj:
            body_content_keys = list(body_content.keys())
            body_content_keys = [
                k for k in body_content_keys if not k.startswith("x-")
            ]
            if len(body_content_keys) == 1:
                mimetype = body_content_keys[0]
                media_type_obj = body_content.get(mimetype, {})

        """xschema_kwargs = row_oas["components"]["schemas"][schema_name][
            "x-schema-kwargs"
        ]"""
        xschema = cast(
            Schema,
            media_type_obj.get("x-schema"),
        )
        if not xschema:
            schema = body_content.get(mimetype, {}).get("schema")
            if schema:
                schema = _resolve_oas_object(row_oas, schema, "schema")
                xschema = cast(
                    Schema,
                    body.get("content", {}).get(mimetype, {}).get("x-schema"),
                )
        return xschema, is_required

    def __validate_request_body(self):
        if self.config.pre_validation_handler:
            self.config.pre_validation_handler()

        try:
            validation_errors = {}
            xschema, is_required = self.__get_request_body_xschema(
                rule_to_path(request.url_rule),
                mimetype=request.mimetype,
                method=request.method,
            )
            body_data = cast(dict, _get_request_body_data())
            if isinstance(
                body_data,
                (
                    str,
                    bytes,
                ),
            ):
                try:
                    body_data = json.loads(body_data)
                except Exception:
                    pass

            if xschema:
                schema = resolve_schema_instance(xschema)

                validation_errors = schema.validate(
                    data=body_data,
                )
            res = self.__post_validation(
                xschema,
                is_required,
                body_data,
                validation_errors,
            )
            if res:
                return res
        except Exception as e:
            print(e)
            warning(e)
        if self.config.post_validation_handler:
            self.config.post_validation_handler()

    def __post_validation(
        self,
        schema: Optional[Schema],
        is_required: bool,
        data: dict,
        errors: dict,
    ) -> Optional[Response]:
        if is_required:
            if errors:
                # abort(make_response(jsonify(errors), HTTPStatus.BAD_REQUEST))
                return make_response(jsonify(errors), HTTPStatus.BAD_REQUEST)
                abort(res)
            elif not schema:
                return make_response(
                    jsonify(
                        {
                            "_schema": "Can't find schema to validate this request"
                        }
                    ),
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                )

        #
        g.setdefault("request_body_data", data)
        g.setdefault("request_body_errors", errors)
        if not schema:
            errors.update(
                {"_schema": "Can't find schema to validate this request"}
            )
            setattr(g, "request_body_errors", errors)


_OpenSpec__RequestsValidator = __RequestsValidator
