from functools import lru_cache
from http import HTTPStatus
from inspect import isclass
from logging import warning
from .plugin.utils import import_by_path, resolve_schema_instance
from typing import TYPE_CHECKING, Optional, cast
from flask import Flask, Response, abort, g, jsonify, make_response

from flask import request_started, request
from marshmallow import Schema

if TYPE_CHECKING:
    from .open_spec import OpenSpec

from ._parameters import rule_to_path


def resolve_schema(oas: dict, schema: dict):
    ref = schema.get("$ref", None)
    if ref:
        rv = ref.split("#/components/schemas/")[-1]
        obj = oas.get("components", {}).get("schemas", {}).get(rv, {})
        return obj
    return schema


class __RequestsValidator:
    def __init__(self, open_spec: "OpenSpec") -> None:
        self.open_spec = open_spec
        self.config = open_spec.config
        if self.config.validate_requests:
            open_spec.app.before_request(self.__validate_request_body)
        else:
            return
        self.row_oas = {}

    def __get_oas_data(self):
        if self.row_oas:
            return self.row_oas
        else:
            self.row_oas = self.open_spec.oas_data
        return self.row_oas

    def __get_request_body_data(self, include_args=False):
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

    def __resolve_request_body(self, rb: dict):
        if not rb:
            return rb
        if rb.get("$ref", None):
            name = rb.get("$ref", "").split("/")[-1]
            return (
                self.__get_oas_data()
                .get("components", {})
                .get("requestBodies", {})
                .get(name, {})
            )
        return rb

    @lru_cache(maxsize=50)
    def __get_request_body_xschema(self, path: str):
        row_oas = self.__get_oas_data()
        mt = request.mimetype
        method = request.method

        if method in ["get", "delete", "head"]:
            return None, False
        body = self.__resolve_request_body(
            (
                row_oas.get("paths", {})
                .get(path, {})
                .get(method.lower(), {})
                .get("requestBody", {})
            )
        )

        if not body:
            return None, False
        is_required = body.get("required", False)

        xschema = ""
        if mt:
            xschema = cast(
                Schema, body.get("content", {}).get(mt, {}).get("x-schema", "")
            )
        else:
            body_content = body.get("content", {})
            body_content_keys = list(body_content.keys())
            body_content_keys = [
                k for k in body_content_keys if not k.startswith("x-")
            ]
            if len(body_content_keys) == 1:
                mt = body_content_keys[0]
            xschema = cast(
                Schema, body.get("content", {}).get(mt, {}).get("x-schema", "")
            )

        """xschema_kwargs = row_oas["components"]["schemas"][schema_name][
            "x-schema-kwargs"
        ]"""
        if not xschema:
            schema = body.get("content", {}).get(mt, {}).get("schema")
            if schema:
                schema = resolve_schema(row_oas, schema)
                xschema = cast(
                    Schema, body.get("content", {}).get(mt, {}).get("x-schema")
                )
        return xschema, is_required

    def __validate_request_body(self):
        if self.config.pre_validattion_handler:
            try:
                self.config.pre_validattion_handler()
            except:
                return
        try:
            validation_errors = {}
            xschema, is_required = self.__get_request_body_xschema(
                rule_to_path(request.url_rule),
            )
            body_data = cast(dict, self.__get_request_body_data())
            print(xschema, is_required, body_data)

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
        if self.config.post_validattion_handler:
            self.config.post_validattion_handler()

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
