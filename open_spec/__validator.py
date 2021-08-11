from enum import Flag
from functools import lru_cache
from http import HTTPStatus
from inspect import isclass
from pprint import pprint, pp
from typing import TYPE_CHECKING, Tuple, cast
from urllib.parse import urlparse
from flask import Flask, Request, Response, abort, g, jsonify, make_response

from flask import request_started, request, current_app
import marshmallow
from marshmallow import Schema, class_registry
from werkzeug.routing import RequestRedirect
from werkzeug.exceptions import MethodNotAllowed, NotFound
from werkzeug.routing import MapAdapter

if TYPE_CHECKING:
    from .open_spec import OpenSpec

from ._parameters import rule_to_path
import importlib


def import_by_path(qualname):
    name = qualname.split(".")[-1]
    path = ".".join(qualname.split(".")[:-1])
    module = importlib.import_module(path)
    obj = getattr(module, name)
    return obj


class __RequestsValidator:
    def __init__(self, open_spec: "OpenSpec") -> None:
        self.open_spec = open_spec
        self.config = open_spec.config
        if self.config.validate_requests:
            request_started.connect(self.__validate_request_body)
        else:
            return
        self.app = open_spec.app
        self.row_oas = {}
        self.final_oas = {}

    def get_row_oas(self):
        if self.row_oas:
            return self.row_oas
        else:
            self.row_oas = self.open_spec.row_data
        return self.row_oas

    def get_final_oas(self):
        if self.final_oas:
            return self.final_oas
        else:
            self.final_oas = self.open_spec.final_oas
        return self.final_oas

    def get_request_body_data(self):
        mt = request.mimetype
        body_data = None

        if request.is_json:
            body_data = request.get_json()
        elif mt in [
            "application/x-www-form-urlencoded",
        ]:
            body_data = request.form
        elif mt in ["multipart/form-data"]:
            body_data = request.files
        else:
            body_data = request.data
        return body_data

    @lru_cache(maxsize=50)
    def get_request_body_schema(self, mt: str, path: str, method: str):
        row_oas = self.get_row_oas()
        # mt = request.mimetype
        # path = rule_to_path(request.url_rule)
        # method = request.method
        if method in ["get", "delete", "head"]:
            return None, False
        body = (
            row_oas.get("paths", {})
            .get(path, {})
            .get(method.lower(), {})
            .get("requestBody", {})
        )
        if not body:
            return None, False
        is_required = body.get("required", False)
        schema = cast(Schema, body.get("content", {}).get(mt, {}).get("schema"))
        return schema, is_required

    def __validate_request_body(self, app: Flask):
        body_data = None
        valid = {}
        schema, is_required = self.get_request_body_schema(
            request.mimetype, rule_to_path(request.url_rule), request.method
        )
        g.request_body_data = None
        g.request_body_data_valid = valid
        g.request_body_data_error = "no schema"
        if schema:
            body_data = cast(dict, self.get_request_body_data())
            valid = schema.validate(data=body_data)
            if valid and is_required:
                res = make_response(jsonify(valid), HTTPStatus.BAD_REQUEST)
                abort(res)
            elif valid:
                schema = cast(Schema, schema)
                body_data = cast(dict, body_data)
                g.request_body_data_error = "invalid"
                g.request_body_data = body_data  # schema.load(body_data)
                g.request_body_data_valid = valid

    def validate_x_schema(self, data, mt):
        x_schema = data.get("content", {}).get(mt, {}).get("x-schema")
        if isinstance(x_schema, str):
            schema_obj = import_by_path(x_schema)
            if isclass(schema_obj):
                valid = schema_obj().validate(body_data)
            else:
                valid = schema_obj.validate(body_data)
            if valid:
                res = make_response(jsonify(valid), HTTPStatus.BAD_REQUEST)
                abort(res)


_OpenSpec__RequestsValidator = __RequestsValidator
