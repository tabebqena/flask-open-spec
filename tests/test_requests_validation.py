from copy import deepcopy
from http import HTTPStatus
import os
import shutil
from marshmallow import Schema, fields
from unittest import TestCase
import json
from flask import Flask, g

from ..open_oas.open_oas import OpenOas


class UserSchema(Schema):
    name = fields.Str(required=True)
    avatar = fields.URL(required=False)


oas_data = {
    "paths": {
        "/users": {
            "post": {
                "requestBody": {
                    "description": "A JSON object containing user information",
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": UserSchema,
                        },
                    },
                },
            },
        },
        "/not_required": {
            "post": {
                "requestBody": {
                    "description": "A JSON object containing user information",
                    "required": False,
                    "content": {
                        "application/json": {
                            "schema": UserSchema,
                        },
                        "text/html": {
                            "schema": UserSchema,
                        },
                    },
                },
            },
        },
    },
}


class TestValidator(TestCase):
    def set_open_oas(self, oas_data):
        self.open_oas = OpenOas(
            app=self.app,
            oas_data=oas_data,
            config_data={
                "OAS_VALIDATE_REQUESTS": True,
                "OAS_DIR": "./test_oas",
                "OAS_VALIDATE_ON_BUILD": False,
            },
        )

    def setUp(self) -> None:
        self.app = Flask(__name__)
        app = self.app
        app.config["debug"] = True
        app.config["TESTING"] = True

        @app.route("/users", methods=["POST"])
        def post_user():
            return ""

        @app.route("/not_required", methods=["POST"])
        def not_required():
            return ""

        return super().setUp()

    def tearDown(self) -> None:
        try:
            file_path = self.open_oas.config.oas_dir_path
            if os.path.exists(file_path):
                shutil.rmtree(file_path)
        except:
            pass

        return super().tearDown()

    def test_no_schema(self):
        _oas_data = deepcopy(oas_data)
        _oas_data["paths"]["/users"]["post"]["requestBody"]["content"][
            "application/json"
        ]["schema"] = {"type": "object"}
        self.set_open_oas(_oas_data)
        data = {"name": "ahmad"}
        with self.app.test_client() as client:
            res = client.post(
                "/users",
                data=json.dumps(data),
                mimetype="application/json",
            )
            self.assertEqual(res.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
            self.assertEqual(
                json.loads(res.get_data()),
                {"_schema": "Can't find schema to validate this request"},
            )

    def test_valid(self):
        data = {"name": "ahmad"}
        self.set_open_oas(oas_data)
        with self.app.test_client() as client:

            res = client.post(
                "/users",
                data=json.dumps(data),
                mimetype="application/json",
            )
            self.assertEqual(res.status_code, HTTPStatus.OK)
            self.assertEqual(g.get("request_body_data"), data)
            self.assertEqual(g.get("request_body_errors"), {})

    def test_invalid(self):
        data = {"name": "ahmad", "tel": 1234}
        self.set_open_oas(oas_data)
        with self.app.test_client() as client:

            res = client.post(
                "/users",
                data=json.dumps(data),
                mimetype="application/json",
            )
            self.assertEqual(res.status_code, HTTPStatus.BAD_REQUEST)
            self.assertNotIn("request_body_data", g)
            self.assertNotIn("request_body_errors", g)

    def test_no_mimetype(self):
        data = {"name": "ahmad"}
        self.set_open_oas(oas_data)
        with self.app.test_client() as client:

            res = client.post(
                "/users",
                data=json.dumps(data),
            )
            self.assertEqual(res.status_code, HTTPStatus.OK)
            self.assertEqual(g.get("request_body_data"), data)
            self.assertEqual(g.get("request_body_errors"), {})

    def test_not_required(self):
        data = {"name": "ahmad"}
        self.set_open_oas(oas_data)
        with self.app.test_client() as client:
            res = client.post(
                "/not_required",
                data=json.dumps(data),
                mimetype="application/json",
            )
            self.assertEqual(res.status_code, HTTPStatus.OK)
            self.assertEqual(g.get("request_body_data"), data)
            self.assertEqual(g.get("request_body_errors"), {})

    def test_not_required_no_schema(self):
        data = {"name": "ahmad"}
        self.set_open_oas(oas_data)
        with self.app.test_client() as client:
            res = client.post(
                "/not_required",
                data=json.dumps(data),
                mimetype="application/xml",
            )
            self.assertEqual(res.status_code, HTTPStatus.OK)
            self.assertEqual(g.get("request_body_data"), data)
            self.assertEqual(
                g.get("request_body_errors"),
                {"_schema": "Can't find schema to validate this request"},
            )
