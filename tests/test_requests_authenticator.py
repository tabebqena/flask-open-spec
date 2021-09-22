from copy import deepcopy
from http import HTTPStatus
from inspect import getmodule
import os
import shutil
from typing import List
from marshmallow import Schema, fields
from unittest import TestCase
import json
from flask import Flask
from flask.wrappers import Response
import pytest
from ..open_oasoopen_oasmport OpenSpec


oas_data = {
    "paths": {
        "/root_security": {"post": {}},
        "/one_schema": {
            "post": {
                "security": [
                    {
                        "QueryApiKey": [],
                    },
                ],
            },
        },
        "/one_many_keys": {
            "post": {
                "security": [
                    {
                        "BearerAuth": [],
                        "BasicAuth": [],
                    },
                ],
            },
        },
        "/many2": {
            "post": {
                "security": [
                    {"HeaderApiKey": []},
                    {"BearerAuth": []},
                ],
            },
        },
        "/many3": {
            "post": {
                "security": [
                    {"HeaderApiKey": []},
                    {"BearerAuth": []},
                    {"BasicAuth": []},
                ],
            },
        },
        "/many_or_one": {
            "post": {
                "security": [
                    {"HeaderApiKey": [], "BearerAuth": []},
                    {"CookieApiKey": []},
                ],
            },
        },
        "/many_or_many": {
            "post": {
                "security": [
                    {"HeaderApiKey": [], "BasicAuth": []},
                    {"CookieApiKey": [], "QueryApiKey": []},
                ],
            },
        },
        "/CookieApiKey": {
            "post": {
                "security": [
                    {"CookieApiKey": []},
                ],
            },
        },
        "/HeaderApiKey": {
            "post": {
                "security": [
                    {"HeaderApiKey": []},
                ],
            },
        },
        "/QueryApiKey": {
            "post": {
                "security": [
                    {"QueryApiKey": []},
                ],
            },
        },
        "/BearerAuth": {
            "post": {
                "security": [
                    {"BearerAuth": []},
                ],
            },
        },
        "/BasicAuth": {
            "post": {
                "security": [
                    {"BasicAuth": []},
                ],
            },
        },
    },
    "components": {
        "securitySchemes": {
            "CookieApiKey": {
                "type": "apiKey",
                "in": "cookie",
                "name": "SecKeyName",
            },
            "HeaderApiKey": {
                "type": "apiKey",
                "in": "header",
                "name": "SecKeyName",
            },
            "QueryApiKey": {
                "type": "apiKey",
                "in": "query",
                "name": "SecKeyName",
            },
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
            },
            "BasicAuth": {
                "type": "http",
                "scheme": "basic",
            },
        },
    },
    "security": [
        {
            "CookieApiKey": [],
        },
    ],
}


def make_app():
    app: Flask = Flask(__name__)

    @app.route("/one_schema", methods=["POST"])
    @app.route("/one_many_keys", methods=["POST"])
    @app.route("/root_security", methods=["POST"])
    @app.route("/many_or_one", methods=["POST"])
    @app.route("/many2", methods=["POST"])
    @app.route("/many3", methods=["POST"])
    @app.route("/many_or_many", methods=["POST"])
    @app.route("/CookieApiKey", methods=["POST"])
    @app.route("/HeaderApiKey", methods=["POST"])
    @app.route("/QueryApiKey", methods=["POST"])
    @app.route("/BearerAuth", methods=["POST"])
    @app.route("/BasicAuth", methods=["POST"])
    def i():
        return "data"

    return app


def false_handler(*args, **kwargs):
    return False


def true_handler(*args, **kwargs):
    return True


class TestAuthenticator(TestCase):
    def setUp(self) -> None:
        self.app = make_app()
        self.default_message = "Test UNAUTHORIZED"
        self.open_oas= OpenSpec(
            app=self.app,
            oas_data=oas_data,
            config_data={
                "OAS_AUTHENTICATE_REQUESTS": True,
                "OAS_DEFAULT_UNAUTHORIZED_MESSAGE": self.default_message,
                "OAS_DIR": "./test_oas",
            },
        )
        with self.app.app_context():
            self.open_oasbuild()
        self.auther = getattr(self.open_oas "_OpenSpec__authenticator")

        return super().setUp()

    def tearDown(self) -> None:
        try:
            file_path = self.open_oasconfig.oas_dir_path
            if os.path.exists(file_path):
                shutil.rmtree(file_path)
        except:
            pass

        return super().tearDown()

    def test_default_on_unauthenticated_handler(self):

        with self.app.app_context():
            res: Response = self.auther._default_on_unauthenticated_handler()
            self.assertIsInstance(res, Response)
            self.assertEqual(res.status_code, HTTPStatus.UNAUTHORIZED)
            self.assertEqual(res.json["message"], self.default_message)  # type: ignore

    def test_get_root_ecurity_scheme(self):

        with self.app.app_context():
            root: dict = self.auther._get_root_security_scheme()
            self.assertEqual(root, oas_data.get("security", {}))

    def test_get_security_schemes(self):
        with self.app.test_request_context():
            sec: dict = self.auther._RequestsAuthenticator__get_path_security_requirements(
                "/one_schema", "post"
            )
            self.assertEqual(
                sec,
                oas_data.get("paths", {})
                .get("/one_schema", {})
                .get("post", {})
                .get("security"),
            )

            sec: dict = self.auther._RequestsAuthenticator__get_path_security_requirements(
                "/root_security", "post"
            )
            self.assertEqual(sec, oas_data.get("security"))
            #
            sec: dict = self.auther._RequestsAuthenticator__get_path_security_requirements(
                "/many_or_one", "post"
            )

            self.assertEqual(
                sec,
                [
                    {
                        "CookieApiKey": [],
                    },
                    {"HeaderApiKey": [], "BearerAuth": []},
                ],
            )


class TestIsRequestAuthenticated(TestCase):
    def setUp(self) -> None:
        self.app = make_app()
        self.default_message = "Test UNAUTHORIZED"
        self.open_oas= OpenSpec(
            app=self.app,
            oas_data=oas_data,
            config_data={
                "OAS_AUTO_BUILD": False,
                "OAS_AUTHENTICATE_REQUESTS": True,
                "OAS_DEFAULT_UNAUTHORIZED_MESSAGE": self.default_message,
                "OAS_DIR": "./test_oas",
            },
        )

        self.auther = getattr(self.open_oas "_OpenSpec__authenticator")

        return super().setUp()

    def tearDown(self) -> None:
        try:
            file_path = self.open_oasconfig.oas_dir_path
            if os.path.exists(file_path):
                shutil.rmtree(file_path)
        except:
            pass

        return super().tearDown()

    def test_is_authenticated_one_schema_valid(self):
        self.open_oasconfig.is_authenticated_handler = true_handler

        c = self.app.test_client()
        with c.post("/one_schema?SecKeyName=1") as res:
            self.assertEqual(res.status_code, 200)

    def test_is_authenticated_one_schema_invalid(self):

        self.open_oasconfig.is_authenticated_handler = false_handler
        c = self.app.test_client()
        with c.post("/one_schema?SecKeyName=1") as res:
            self.assertEqual(res.status_code, HTTPStatus.UNAUTHORIZED)


class TestParseInfo(TestCase):
    def setUp(self) -> None:
        self.app = make_app()
        self.default_message = "Test UNAUTHORIZED"
        self.open_oas= OpenSpec(
            app=self.app,
            oas_data=oas_data,
            config_data={
                "OAS_AUTHENTICATE_REQUESTS": True,
                "OAS_DEFAULT_UNAUTHORIZED_MESSAGE": self.default_message,
                "OAS_DIR": "./test_oas",
            },
        )
        with self.app.app_context():
            self.open_oasbuild()
        self.auther = getattr(self.open_oas "_OpenSpec__authenticator")
        self.parser = self.auther._RequestsAuthenticator__parse_scheme_info

        return super().setUp()

    def tearDown(self) -> None:
        try:
            file_path = self.open_oasconfig.oas_dir_path
            if os.path.exists(file_path):
                shutil.rmtree(file_path)
        except:
            pass

        return super().tearDown()

    def test_parse_api_cookie(self):
        with self.app.test_client() as c:
            name = "CookieApiKey"
            val = "1"
            c.set_cookie("localhost", "SecKeyName", val)

            with c.post(f"/{name}"):
                data = (
                    self.open_oasget_spec_dict()
                    .get("components", {})
                    .get("securitySchemes", {})
                    .get(name, {})
                )
                self.assertEqual(self.parser(data), val)

    def test_parse_api_header(self):
        name = "HeaderApiKey"
        with self.app.test_client() as c:
            val = "1"
            headers = {"SecKeyName": val}

            with c.post(f"/{name}", headers=headers):
                data = (
                    self.open_oasget_spec_dict()
                    .get("components", {})
                    .get("securitySchemes", {})
                    .get(name, {})
                )
                self.assertEqual(self.parser(data), val)

    def test_parse_api_query(self):
        name = "QueryApiKey"
        with self.app.test_client() as c:
            val = "1"
            query = {"SecKeyName": val}

            with c.post(f"/{name}", query_string=query):
                data = (
                    self.open_oasget_spec_dict()
                    .get("components", {})
                    .get("securitySchemes", {})
                    .get(name, {})
                )
                self.assertEqual(self.parser(data), val)

    def test_parse_bearer(self):
        name = "BearerAuth"
        with self.app.test_client() as c:
            val = "1"
            headers = {"Authorization": f"Bearer {val}"}

            with c.post(f"/{name}", headers=headers):
                data = (
                    self.open_oasget_spec_dict()
                    .get("components", {})
                    .get("securitySchemes", {})
                    .get(name, {})
                )
                self.assertEqual(self.parser(data), val)

    def test_parse_basic(self):
        name = "BasicAuth"
        with self.app.test_client() as c:
            val = "1"
            headers = {"Authorization": f"Basic {val}"}

            with c.post(f"/{name}", headers=headers):
                data = (
                    self.open_oasget_spec_dict()
                    .get("components", {})
                    .get("securitySchemes", {})
                    .get(name, {})
                )
                self.assertEqual(self.parser(data), val)


class TestAuthenticateRequests(TestCase):
    def setUp(self) -> None:
        self.app = make_app()
        self.default_message = "Test UNAUTHORIZED"
        self.open_oas= OpenSpec(
            app=self.app,
            oas_data=oas_data,
            config_data={
                "OAS_AUTO_BUILD": True,
                "OAS_AUTHENTICATE_REQUESTS": True,
                "OAS_DEFAULT_UNAUTHORIZED_MESSAGE": self.default_message,
                "OAS_DIR": "./test_oas",
            },
        )
        with self.app.app_context():
            self.open_oasbuild()

        self.auther = getattr(self.open_oas "_OpenSpec__authenticator")
        self.auther.row_oas = self.open_oasget_spec_dict()

        self.schemes = [
            "CookieApiKey",
            "HeaderApiKey",
            "QueryApiKey",
            "BearerAuth",
            "BasicAuth",
        ]
        self.paths = [
            "/root_security",
            "/one_schema",
            "/one_many_keys",
            "/many2",
            "/many3",
            "/many_or_one",
            "/many_or_many",
            "/CookieApiKey",
            "/HeaderApiKey",
            "/QueryApiKey",
            "/BearerAuth",
            "/BasicAuth",
        ]

        return super().setUp()

    def tearDown(self) -> None:
        try:
            file_path = self.open_oasconfig.oas_dir_path
            if os.path.exists(file_path):
                shutil.rmtree(file_path)
        except:
            pass

        return super().tearDown()

    # runtime changes of security schemes x-handler key
    # call all paths
    # check status for every
    def set_xhandler(self, scheme_names: List[str], xhandler):
        qualname = getattr(xhandler, "__module__", "") + "." + xhandler.__name__
        # oas = self.open_oasget_spec_dict()
        for name in scheme_names:
            orig = (
                self.auther.row_oas.get("components", {})
                .get("securitySchemes", {})
                .get(name, {})
            )
            orig["x-handler"] = qualname

    def test_all_false(self):
        expected = {}
        for p in self.paths:
            expected[p] = False

        self.set_xhandler(self.schemes, false_handler)

        client = self.app.test_client()
        for p, v in expected.items():
            with client.post(p) as res:
                # if v:
                #    self.assertEqual(res.status_code, 200)
                # else:
                self.assertEqual(res.status_code, 401)

    def test_all_true(self):
        expected = {}
        for p in self.paths:
            expected[p] = True

        self.set_xhandler(self.schemes, true_handler)

        client = self.app.test_client()
        for p, v in expected.items():
            with client.post(p) as res:
                self.assertEqual(res.status_code, 200)

    def test_cookie_key_is_false(self):
        unauthenticated = [
            "/root_security",
            "/CookieApiKey",
        ]
        expected = {}
        for p in self.paths:
            if p in unauthenticated:
                expected[p] = False
            else:
                expected[p] = True
        self.set_xhandler(self.schemes, true_handler)
        self.set_xhandler(["CookieApiKey"], false_handler)

        client = self.app.test_client()
        items = list(expected.items())

        for p, v in items:
            with client.post(p) as res:
                if v:
                    self.assertEqual(res.status_code, 200)
                else:
                    self.assertEqual(res.status_code, 401)

    def test_header_key_is_false(self):
        unauthenticated = ["/HeaderApiKey"]
        expected = {}
        for p in self.paths:
            if p in unauthenticated:
                expected[p] = False
            else:
                expected[p] = True
        self.set_xhandler(self.schemes, true_handler)
        self.set_xhandler(["HeaderApiKey"], false_handler)

        client = self.app.test_client()
        items = list(expected.items())

        for p, v in items:
            with client.post(p) as res:
                if v:
                    self.assertEqual(res.status_code, 200)
                else:
                    self.assertEqual(res.status_code, 401)

    def test_query_key_is_false(self):
        unauthenticated = [
            "/one_schema",
            "/QueryApiKey",
        ]
        expected = {}
        for p in self.paths:
            if p in unauthenticated:
                expected[p] = False
            else:
                expected[p] = True
        self.set_xhandler(self.schemes, true_handler)
        self.set_xhandler(["QueryApiKey"], false_handler)

        client = self.app.test_client()
        items = list(expected.items())

        for p, v in items:
            with client.post(p) as res:
                if v:
                    self.assertEqual(res.status_code, 200)
                else:
                    self.assertEqual(res.status_code, 401)

    def test_bearer_key_is_false(self):
        unauthenticated = [
            "/BearerAuth",
            "/one_many_keys",
        ]
        expected = {}
        for p in self.paths:
            if p in unauthenticated:
                expected[p] = False
            else:
                expected[p] = True
        self.set_xhandler(self.schemes, true_handler)
        self.set_xhandler(["BearerAuth"], false_handler)

        client = self.app.test_client()
        items = list(expected.items())

        for p, v in items:
            with client.post(p) as res:
                if v:
                    self.assertEqual(res.status_code, 200)
                else:
                    self.assertEqual(res.status_code, 401)

    def test_basic_key_is_false(self):
        unauthenticated = [
            "/BasicAuth",
            "/one_many_keys",
        ]
        expected = {}
        for p in self.paths:
            if p in unauthenticated:
                expected[p] = False
            else:
                expected[p] = True
        self.set_xhandler(self.schemes, true_handler)
        self.set_xhandler(["BasicAuth"], false_handler)

        client = self.app.test_client()
        items = list(expected.items())

        for p, v in items:
            with client.post(p) as res:
                if v:
                    self.assertEqual(res.status_code, 200)
                else:
                    self.assertEqual(res.status_code, 401)

    def test_basic_and_bearer_are_false(self):
        unauthenticated = [
            "/BasicAuth",
            "/BearerAuth",
            "/one_many_keys",
        ]
        expected = {}
        for p in self.paths:
            if p in unauthenticated:
                expected[p] = False
            else:
                expected[p] = True
        self.set_xhandler(self.schemes, true_handler)
        self.set_xhandler(["BasicAuth", "BearerAuth"], false_handler)

        client = self.app.test_client()
        items = list(expected.items())

        for p, v in items:
            with client.post(p) as res:
                if v:
                    self.assertEqual(res.status_code, 200)
                else:
                    self.assertEqual(res.status_code, 401)

    def test_header_key_and_bearer_are_false(self):
        unauthenticated = [
            "/many2",
            "/HeaderApiKey",
            "/BearerAuth",
            "/one_many_keys",
        ]
        expected = {}
        for p in self.paths:
            if p in unauthenticated:
                expected[p] = False
            else:
                expected[p] = True
        self.set_xhandler(self.schemes, true_handler)
        self.set_xhandler(["HeaderApiKey", "BearerAuth"], false_handler)

        client = self.app.test_client()
        items = list(expected.items())

        for p, v in items:
            with client.post(p) as res:
                if v:
                    self.assertEqual(res.status_code, 200)
                else:
                    self.assertEqual(res.status_code, 401)

    def test_header_key_and_basic_are_false(self):
        unauthenticated = [
            "/one_many_keys",
            "/HeaderApiKey",
            "/BasicAuth",
        ]
        expected = {}
        for p in self.paths:
            if p in unauthenticated:
                expected[p] = False
            else:
                expected[p] = True
        self.set_xhandler(self.schemes, true_handler)
        self.set_xhandler(["HeaderApiKey", "BasicAuth"], false_handler)

        client = self.app.test_client()
        items = list(expected.items())

        for p, v in items:
            with client.post(p) as res:
                if v:
                    self.assertEqual(res.status_code, 200)
                else:
                    self.assertEqual(res.status_code, 401)

    def test_header_key_and_query_key_are_false(self):
        unauthenticated = [
            "/QueryApiKey",
            "/one_schema",
            "/many_or_many",
            "/HeaderApiKey",
            "/QueryApiKey",
        ]
        expected = {}
        for p in self.paths:
            if p in unauthenticated:
                expected[p] = False
            else:
                expected[p] = True
        self.set_xhandler(self.schemes, true_handler)
        self.set_xhandler(["HeaderApiKey", "QueryApiKey"], false_handler)

        client = self.app.test_client()
        items = list(expected.items())

        for p, v in items:
            with client.post(p) as res:
                if v:
                    self.assertEqual(res.status_code, 200)
                else:
                    self.assertEqual(res.status_code, 401)

    def test_cookie_key_and_query_are_false(self):
        unauthenticated = [
            "/root_security",
            "/one_schema",
            "/CookieApiKey",
            "/QueryApiKey",
        ]
        expected = {}
        for p in self.paths:
            if p in unauthenticated:
                expected[p] = False
            else:
                expected[p] = True
        self.set_xhandler(self.schemes, true_handler)
        self.set_xhandler(["CookieApiKey", "QueryApiKey"], false_handler)

        client = self.app.test_client()
        items = list(expected.items())

        for p, v in items:
            with client.post(p) as res:
                if v:
                    self.assertEqual(res.status_code, 200)
                else:
                    self.assertEqual(res.status_code, 401)

    def test_cookie_key_and_header_key_are_false(self):
        unauthenticated = [
            "/root_security",
            "/many_or_one",
            "/many_or_many",
            "/CookieApiKey",
            "/HeaderApiKey",
        ]
        expected = {}
        for p in self.paths:
            if p in unauthenticated:
                expected[p] = False
            else:
                expected[p] = True
        self.set_xhandler(self.schemes, true_handler)
        self.set_xhandler(["CookieApiKey", "HeaderApiKey"], false_handler)

        client = self.app.test_client()
        items = list(expected.items())

        for p, v in items:
            with client.post(p) as res:
                if v:
                    self.assertEqual(res.status_code, 200)
                else:
                    self.assertEqual(res.status_code, 401)

    def test_cookie_key_and_query_key_are_false(self):
        unauthenticated = [
            "/root_security",
            "/one_schema",
            "/CookieApiKey",
            "/QueryApiKey",
        ]
        expected = {}
        for p in self.paths:
            if p in unauthenticated:
                expected[p] = False
            else:
                expected[p] = True
        self.set_xhandler(self.schemes, true_handler)
        self.set_xhandler(["CookieApiKey", "QueryApiKey"], false_handler)

        client = self.app.test_client()
        items = list(expected.items())

        for p, v in items:
            with client.post(p) as res:
                if v:
                    self.assertEqual(res.status_code, 200)
                else:
                    self.assertEqual(res.status_code, 401)

    def test_cookie_key_and_basic_are_false(self):
        unauthenticated = [
            "/root_security",
            "/many_or_many",
            "/one_many_keys",
            "/CookieApiKey",
            "/BasicAuth",
        ]
        expected = {}
        for p in self.paths:
            if p in unauthenticated:
                expected[p] = False
            else:
                expected[p] = True
        self.set_xhandler(self.schemes, true_handler)
        self.set_xhandler(["CookieApiKey", "BasicAuth"], false_handler)

        client = self.app.test_client()
        items = list(expected.items())

        for p, v in items:
            with client.post(p) as res:
                if v:
                    self.assertEqual(res.status_code, 200)
                else:
                    self.assertEqual(res.status_code, 401)

    def test_cookie_key_and_bearer_are_false(self):
        unauthenticated = [
            "/root_security",
            "/one_many_keys",
            "/many_or_one",
            "/CookieApiKey",
            "/BearerAuth",
        ]
        expected = {}
        for p in self.paths:
            if p in unauthenticated:
                expected[p] = False
            else:
                expected[p] = True
        self.set_xhandler(self.schemes, true_handler)
        self.set_xhandler(["CookieApiKey", "BearerAuth"], false_handler)

        client = self.app.test_client()
        items = list(expected.items())

        for p, v in items:
            with client.post(p) as res:
                if v:
                    self.assertEqual(res.status_code, 200)
                else:
                    self.assertEqual(res.status_code, 401)

    def test_header_bearer_basic_are_false(self):
        unauthenticated = [
            "/one_many_keys",
            "/many2",
            "/many3",
            "/BasicAuth",
            "/HeaderApiKey",
            "/BearerAuth",
        ]
        expected = {}
        for p in self.paths:
            if p in unauthenticated:
                expected[p] = False
            else:
                expected[p] = True
        self.set_xhandler(self.schemes, true_handler)
        self.set_xhandler(
            ["HeaderApiKey", "BasicAuth", "BearerAuth"], false_handler
        )

        client = self.app.test_client()
        items = list(expected.items())

        for p, v in items:
            with client.post(p) as res:
                if v:
                    self.assertEqual(res.status_code, 200)
                else:
                    self.assertEqual(res.status_code, 401)
