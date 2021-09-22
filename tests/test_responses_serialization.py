from copy import deepcopy
from dataclasses import dataclass
from http import HTTPStatus
from ntpath import join
import os
import shutil
from marshmallow import Schema, fields
from unittest import TestCase
import json
from flask import Flask, g, redirect as flask_redirect
import pytest

from ..open_oas import OpenOas


@dataclass
class User:
    id: int
    name: str
    avatar: str


@dataclass
class VerboseUser:
    id: int
    name: str
    avatar: str
    tel: str


@dataclass
class BreifUser:
    id: int
    name: str


class UserSchema(Schema):
    id = fields.Integer(required=True)
    name = fields.Str(required=True)
    avatar = fields.URL(required=False)


oas_data = {
    "components": {
        "responses": {
            "User": {
                "description": "OK",
                "content": {
                    "application/json": {
                        "schema": UserSchema,
                    }
                },
            },
        }
    },
    "paths": {
        "/users": {
            "post": {
                "responses": {
                    "200": {
                        "description": "OK",
                        "content": {
                            "application/json": {
                                "schema": UserSchema,
                            },
                            "application/xml": {
                                "schema": UserSchema,
                            },
                            "application/x-www-form-urlencoded": {
                                "schema": UserSchema,
                            },
                        },
                    }
                },
            },
        },
        "/verbose": {
            "post": {
                "responses": {
                    "200": {
                        "description": "OK",
                        "content": {
                            "application/json": {
                                "schema": UserSchema,
                            },
                        },
                    }
                },
            },
        },
        "/breif": {
            "post": {
                "responses": {
                    "200": {
                        "description": "OK",
                        "content": {
                            "application/json": {
                                "schema": UserSchema,
                            },
                        },
                    }
                },
            },
        },
        "/range": {
            "post": {
                "responses": {
                    "2XX": {
                        "description": "Error",
                        "content": {
                            "application/json": {
                                "schema": UserSchema,
                            }
                        },
                    }
                },
            },
        },
        "/default": {
            "post": {
                "responses": {
                    "default": {
                        "description": "OK",
                        "content": {
                            "application/json": {
                                "schema": UserSchema,
                            }
                        },
                    }
                },
            },
        },
        "/no_response": {
            "post": {
                "responses": {},
            },
        },
        "/no_response_error": {
            "post": {
                "responses": {},
            },
        },
        "/reused": {
            "post": {
                "responses": {
                    "default": {"$ref": "#/components/responses/User"},
                },
            },
        },
        "no_content": {
            "post": {
                "responses": {
                    "default": {"description": "OK", "content": {}},
                }
            },
        },
        "no_content_error": {
            "post": {
                "responses": {
                    "default": {"description": "OK", "content": {}},
                }
            },
        },
        "/explicit_mimetype": {
            "post": {
                "responses": {
                    "default": {
                        "description": "OK",
                        "content": {
                            "application/xml": {
                                "schema": UserSchema,
                            },
                            "application/xml2": {
                                "schema": UserSchema,
                            },
                        },
                    }
                },
            },
        },
    },
}


class TestSerializer(TestCase):
    def set_open_oas(self, oas_data):
        self.open_oas = OpenOas(
            app=self.app,
            oas_data=oas_data,
            config_data={
                "OAS_SERIALIZE_RESPONSE": True,
                "OAS_DIR": "./test_oas",
                "OAS_VALIDATE_ON_BUILD": False,
                "OAS_FILE_SAVE": False,
            },
        )

    def setUp(self) -> None:
        self.app = Flask(__name__)
        app = self.app
        app.config["debug"] = True
        app.config["TESTING"] = True
        self.data = {"id": 1, "name": "ahmad", "avatar": "http://avatar"}

        # app.before_request(lambda: print(request.__dict__))

        @app.route("/users", methods=["POST"])
        def post_user():
            u = User(**self.data)
            return u

        @app.route("/verbose", methods=["POST"])
        def verbose():
            u = VerboseUser(**self.data, tel="12345")
            return u

        @app.route("/range", methods=["POST"])
        def range():
            u = User(**self.data)
            return u

        @app.route("/breif", methods=["POST"])
        def breif():
            u = BreifUser(id=self.data["id"], name=self.data["name"])
            return u

        @app.route("/no_response", methods=["POST"])
        def no_response():
            return {"data": None}

        @app.route("/no_response_error", methods=["POST"])
        def no_response_error():
            u = User(**self.data)
            return u

        @app.route("/default", methods=["POST"])
        def default():
            u = User(**self.data)
            return u

        @app.route("/no_content", methods=["POST"])
        def no_content():
            return {"data": None}

        @app.route("/no_content_error", methods=["POST"])
        def no_content_error():
            u = User(**self.data)
            return u

        @app.route("/explicit_mimetype", methods=["POST"])
        def explicit_mimetype():
            u = User(**self.data)
            return u, {"Content-Type": "application/xml2"}

        return super().setUp()

    def tearDown(self) -> None:
        try:
            file_path = self.open_oas.config.oas_dir_path
            if os.path.exists(file_path):
                shutil.rmtree(file_path)
        except:
            pass

        return super().tearDown()

    def test_users(self):
        self.set_open_oas(oas_data)
        with self.app.test_client() as client:
            res = client.post("/users")
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.get_json(), self.data)

    def test_verbose(self):
        self.set_open_oas(oas_data)
        with self.app.test_client() as client:
            res = client.post(
                "/verbose",
            )
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.get_json(), self.data)

    def test_breif(self):
        self.set_open_oas(oas_data)
        with self.app.test_client() as client:
            res = client.post(
                "/breif",
            )
            self.assertEqual(res.status_code, 200)
            self.assertEqual(
                res.get_json(),
                {"id": self.data["id"], "name": self.data["name"]},
            )

    def test_range_status_code_response(self):
        self.set_open_oas(oas_data)
        with self.app.test_client() as client:
            res = client.post("/range")
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.get_json(), self.data)

    def test_default_response(self):

        self.set_open_oas(oas_data)
        with self.app.test_client() as client:
            res = client.post("/default")
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.get_json(), self.data)

    def test_reused_response(self):

        self.set_open_oas(oas_data)
        with self.app.test_client() as client:
            res = client.post("/users")
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.get_json(), self.data)

    def test_no_response(self):

        self.set_open_oas(oas_data)
        with self.app.test_client() as client:
            res = client.post("/no_response")
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.get_json(), {"data": None})

    def test_no_response_error(self):
        self.set_open_oas(oas_data)
        with self.assertRaises(TypeError):
            client = self.app.test_client()
            client.post("/no_response_error")

    def test_no_content_response(self):

        self.set_open_oas(oas_data)
        with self.app.test_client() as client:
            res = client.post("/no_content")
            self.assertEqual(res.status_code, 200)

    def test_no_content_response_error(self):

        self.set_open_oas(oas_data)
        with self.assertRaises(TypeError):
            client = self.app.test_client()
            client.post("/no_content_error")

    def test_explicit_mimetype(self):

        self.set_open_oas(oas_data)
        with self.app.test_client() as client:
            res = client.post("/explicit_mimetype")
            self.assertEqual(res.status_code, 200)
            data = res.get_data()

            self.assertEqual(json.loads(data), self.data)
