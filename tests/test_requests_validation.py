from copy import deepcopy
from http import HTTPStatus
import os
import shutil
from marshmallow import Schema, fields
from ..open_spec.oas_config import OasConfig
from unittest import TestCase
import json
from flask import Flask, g

from ..open_spec.open_spec import OpenSpec


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
    },
}


class TestValidator(TestCase):
    def set_open_spec(self, oas_data):
        self.open_spec = OpenSpec(
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

        return super().setUp()

    def tearDown(self) -> None:
        file_path = self.open_spec.config.oas_dir_path
        if os.path.exists(file_path):
            shutil.rmtree(file_path)

        return super().tearDown()

    def test_no_schema(self):
        _oas_data = deepcopy(oas_data)
        _oas_data["paths"]["/users"]["post"]["requestBody"]["content"][
            "application/json"
        ]["schema"] = {"type": "object"}
        self.set_open_spec(_oas_data)
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
        self.set_open_spec(oas_data)
        with self.app.test_client() as client:

            res = client.post(
                "/users",
                data=json.dumps(data),
                mimetype="application/json",
            )
            print(res.data)
            self.assertEqual(res.status_code, HTTPStatus.OK)
            self.assertEqual(g.get("request_body_data"), data)
            self.assertEqual(g.get("request_body_errors"), {})

    def test_invalid(self):
        data = {"name": "ahmad", "tel": 1234}
        self.set_open_spec(oas_data)
        with self.app.test_client() as client:

            res = client.post(
                "/users",
                data=json.dumps(data),
                mimetype="application/json",
            )
            self.assertEqual(res.status_code, HTTPStatus.BAD_REQUEST)
            self.assertNotIn("request_body_data", g)
            self.assertNotIn("request_body_errors", g)
