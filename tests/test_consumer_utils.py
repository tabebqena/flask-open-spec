from http.client import responses
from unittest import TestCase
from flask import Flask
from werkzeug.datastructures import Headers
from http import HTTPStatus
from ..open_oas.open_oas.consumer._utils import (
    _parse_status,
    _parse_headers,
    _resolve_oas_object,
    _get_best_response,
    _get_best_media_type_object,
    _get_mimetype,
    _parse_view_function_res,
)
from .schemas.schemas import UserSchema

from werkzeug.wrappers import Response as BaseResponse


def test_resolve_schema1():
    schema = {"type": "object", "properties": {"id": {"type": "string"}}}
    data = {
        "components": {},
        "paths": {"/gists": {"post": {"requestBody": {"schema": schema}}}},
    }
    assert (
        _resolve_oas_object(
            data,
            data.get("paths", {})
            .get("/gists", {})
            .get("post", {})
            .get("requestBody", {})
            .get("schema", {}),
            "schemas",
        )
        == schema
    )


def test_resolve_schema2():
    schema = {"type": "object", "properties": {"id": {"type": "string"}}}
    data = {
        "components": {
            "schemas": {"Gist": schema},
        },
        "paths": {
            "/gists": {
                "post": {
                    "requestBody": {
                        "schema": {"$ref": "#/components/schemas/Gist"}
                    }
                }
            }
        },
    }
    assert (
        _resolve_oas_object(
            data,
            data.get("paths", {})
            .get("/gists", {})
            .get("post", {})
            .get("requestBody", {})
            .get("schema", {}),
            "schema",
        )
        == schema
    )


def test_parse_status_int():
    assert _parse_status(404) == HTTPStatus.NOT_FOUND
    assert _parse_status(500) == HTTPStatus.INTERNAL_SERVER_ERROR
    assert _parse_status(408) == HTTPStatus.REQUEST_TIMEOUT


def test_parse_status_none():
    assert _parse_status(None) == HTTPStatus.OK
    assert _parse_status() == HTTPStatus.OK


def test_parse_status_statua():
    assert _parse_status(HTTPStatus.OK) == HTTPStatus.OK
    assert (
        _parse_status(HTTPStatus.INSUFFICIENT_STORAGE)
        == HTTPStatus.INSUFFICIENT_STORAGE
    )
    assert (
        _parse_status(HTTPStatus.INTERNAL_SERVER_ERROR)
        == HTTPStatus.INTERNAL_SERVER_ERROR
    )
    assert (
        _parse_status(HTTPStatus.REQUEST_TIMEOUT) == HTTPStatus.REQUEST_TIMEOUT
    )


def test_parse_headers_headers():
    headers = Headers()
    headers.add("Content_type", "application/json")

    assert _parse_headers(headers) == headers
    assert _parse_headers(headers).get("Content_type") == "application/json"


def test_parse_headers_tuple():
    _headers = (
        ("Content_type", "application/json"),
        ("Proxy-Connection", "Keep-Alive"),
    )
    expected = Headers(
        {"Content_type": "application/json", "Proxy-Connection": "Keep-Alive"}
    )

    assert _parse_headers(_headers).get("Content_type") == expected.get(
        "Content_type"
    )
    assert _parse_headers(_headers).get("Proxy-Connection") == expected.get(
        "Proxy-Connection"
    )


def test_parse_headers_dict():
    _headers = {
        "Content_type": "application/json",
        "Proxy-Connection": "Keep-Alive",
    }
    expected = Headers(
        {"Content_type": "application/json", "Proxy-Connection": "Keep-Alive"}
    )

    assert _parse_headers(_headers).get("Content_type") == expected.get(
        "Content_type"
    )
    assert _parse_headers(_headers).get("Proxy-Connection") == expected.get(
        "Proxy-Connection"
    )


def test_parse_headers_list():
    _headers = [
        ("Content_type", "application/json"),
        ("Proxy-Connection", "Keep-Alive"),
    ]
    expected = Headers(
        {"Content_type": "application/json", "Proxy-Connection": "Keep-Alive"}
    )

    assert _parse_headers(_headers).get("Content_type") == expected.get(
        "Content_type"
    )
    assert _parse_headers(_headers).get("Proxy-Connection") == expected.get(
        "Proxy-Connection"
    )


def test_resolve_response1():
    response = {
        "description": "OK",
        "content": {
            "application/json": {
                "schema": {"type": "object"},
            },
            "application/xml": {
                "schema": {"type": "object"},
            },
        },
    }
    data = {
        "components": {},
        "paths": {"/gists": {"post": {"responses": {"200": response}}}},
    }
    assert (
        _resolve_oas_object(
            data,
            data.get("paths", {})
            .get("/gists", {})
            .get("post", {})
            .get("responses", {})
            .get("200", {}),
            "response",
        )
        == response
    )


def test_resolve_response2():
    response = {
        "description": "OK",
        "content": {
            "application/json": {
                "schema": {"type": "object"},
            },
            "application/xml": {
                "schema": {"type": "object"},
            },
        },
    }
    data = {
        "components": {"responses": {"Gist": response}},
        "paths": {
            "/gists": {
                "post": {
                    "responses": {
                        "200": {"$ref": "#/components/responses/Gist"},
                    },
                },
            },
        },
    }
    assert (
        _resolve_oas_object(
            data,
            data.get("paths", {})
            .get("/gists", {})
            .get("post", {})
            .get("responses", {})
            .get("200", {}),
            "response",
        )
        == response
    )


def test_resolve_request_body1():
    req = {
        "description": "gist request body",
        "required": True,
        "content": {
            "application/json": {
                "schema": {"type": "object"},
            },
            "application/xml": {
                "schema": {"type": "object"},
            },
        },
    }
    data = {
        "components": {},
        "paths": {"/gists": {"post": {"requestBody": req}}},
    }
    assert (
        _resolve_oas_object(
            data,
            data.get("paths", {})
            .get("/gists", {})
            .get("post", {})
            .get("requestBody", {}),
            "rb",
        )
        == req
    )


def test_resolve_request_body2():
    req = {
        "description": "gist request body",
        "required": True,
        "content": {
            "application/json": {
                "schema": {"type": "object"},
            },
            "application/xml": {
                "schema": {"type": "object"},
            },
        },
    }
    data = {
        "components": {"requestBodies": {"Gist": req}},
        "paths": {
            "/gists": {
                "post": {
                    "requestBody": {"$ref": "#/components/requestBodies/Gist"}
                }
            }
        },
    }
    assert (
        _resolve_oas_object(
            data,
            data.get("paths", {})
            .get("/gists", {})
            .get("post", {})
            .get("requestBody", {}),
            "rb",
        )
        == req
    )


class BestTest(TestCase):
    def setUp(self) -> None:
        self.response = {
            "description": "OK",
            "content": {
                "application/json": {
                    "schema": UserSchema,
                },
            },
        }
        return super().setUp()

    def test_best_response(self):
        responses = {"200": self.response}
        self.assertEqual(
            _get_best_response(responses, HTTPStatus.OK), self.response
        )
        responses = {200: self.response}

        self.assertEqual(
            _get_best_response(responses, HTTPStatus.OK), self.response
        )
        responses = {"2XX": self.response}

        self.assertEqual(
            _get_best_response(responses, HTTPStatus.OK), self.response
        )

        responses = {"2xx": self.response}

        self.assertEqual(
            _get_best_response(responses, HTTPStatus.OK), self.response
        )

        responses = {"default": self.response}

        self.assertEqual(
            _get_best_response(responses, HTTPStatus.OK), self.response
        )
        responses = {"default": self.response}

        self.assertEqual(
            _get_best_response(responses, HTTPStatus.SERVICE_UNAVAILABLE),
            self.response,
        )


class BestMTO(TestCase):
    def setUp(self) -> None:
        self.response = {
            "content": {
                "application/json": {
                    "schema": {"index": 0},
                },
                "text/*": {
                    "schema": {"index": 1},
                },
                "text/html": {
                    "schema": {"index": 2},
                },
                "image/*": {
                    "schema": {"index": 3},
                },
            },
        }
        return super().setUp()

    def test_with_mimetype(self):
        self.assertEqual(
            _get_best_media_type_object(self.response, "application/json"),
            self.response.get("content", {}).get("application/json"),
        )

    def test_with_starred_mimetype(self):
        self.assertEqual(
            _get_best_media_type_object(self.response, "image/png"),
            self.response.get("content", {}).get("image/*"),
        )

    def test_with_no_mimetype_with_accepts(self):
        self.assertEqual(
            _get_best_media_type_object(self.response, None, "text/*"),
            self.response.get("content", {}).get("text/*"),
        )

    def test_with_no_mimetype_no_accepts(self):
        expected = []
        for k in self.response.get("content", {}).keys():
            expected.append(self.response.get("content", {})[k])
        self.assertIn(
            _get_best_media_type_object(self.response, None, None), expected
        )


class GetMimetype(TestCase):
    def test_starred_accept_single(self):
        keys = ["text/html", "invalid/invalid", "invalid/*"]
        accepts = "text/*"
        res = _get_mimetype(keys, accepts)
        self.assertEqual(res, "text/html")

    def test_starred_accept_multiple1(self):
        keys = ["text/html", "text/string", "invalid/invalid", "invalid/*"]
        accepts = "text/*"
        res = _get_mimetype(keys, accepts)
        self.assertEqual(res, "text/html")

    def test_starred_accept_multiple2(self):
        keys = [
            "text/string",
            "invalid/invalid",
            "invalid/*",
            "application/json",
        ]
        accepts = "application/*, text/*, "
        res = _get_mimetype(keys, accepts)
        self.assertEqual(res, "application/json")

    def test_explicit_accept_single(self):
        keys = ["text/html", "invalid/invalid", "invalid/*"]
        accepts = "text/html"
        res = _get_mimetype(keys, accepts)
        self.assertEqual(res, "text/html")

    def test_explicit_accept_single2(self):
        keys = ["invalid/invalid", "invalid/*", "text/html"]
        accepts = "text/html"
        res = _get_mimetype(keys, accepts)
        self.assertEqual(res, "text/html")

    def test_explicit_accept_multiple(self):
        keys = ["text/html", "invalid/invalid", "invalid/*", "application/json"]
        accepts = "text/html, application/json"
        res = _get_mimetype(keys, accepts)
        self.assertEqual(res, "text/html")


class ParseRVTest(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def run_test_headers(self, res):
        self.assertIsInstance(
            res[2],
            Headers,
        )
        self.assertEqual(
            res[2].get("Header"),
            "Header-Value",
        )

    def test_empty(self):
        rv = {}
        with self.assertRaises(TypeError):
            _parse_view_function_res(
                rv, Flask.response_class, "application/json"
            )

    def test_none(self):
        rv = None

        with self.assertRaises(TypeError):
            _parse_view_function_res(
                rv, Flask.response_class, "application/json"
            )

    def test_response_class(self):
        rv = Flask.response_class()

        with self.assertRaises(TypeError):
            _parse_view_function_res(
                rv, Flask.response_class, "application/json"
            )

    def test_base_response_class(self):
        rv = BaseResponse()

        with self.assertRaises(TypeError):
            _parse_view_function_res(
                rv, Flask.response_class, "application/json"
            )

    def test_callable(self):
        rv = lambda x: x

        with self.assertRaises(TypeError):
            _parse_view_function_res(
                rv, Flask.response_class, "application/json"
            )

    def test_3_tuple(self):
        rv = ("data", 200, {"Header": "Header-Value"})
        def_mime = "application/json"
        # rv, status, headers, mimetype
        res = _parse_view_function_res(rv, Flask.response_class, def_mime)

        self.assertEqual(
            res[0],
            (rv[0]),
        )
        self.assertEqual(res[1], 200)

        self.run_test_headers(res)
        self.assertEqual(
            res[3],
            def_mime,
        )

    def test_2_tuple_status(self):
        """if isinstance(rv[1], (Headers, dict, tuple, list)):
            rv, headers = rv
        else:
            rv, status = rv"""
        rv = ("data", 200)
        def_mime = "application/json"
        # rv, status, headers, mimetype
        res = _parse_view_function_res(rv, Flask.response_class, def_mime)

        self.assertEqual(
            res[0],
            (rv[0]),
        )
        self.assertEqual(res[1], 200)
        self.assertIsInstance(
            res[2],
            Headers,
        )

    def test_2_tuple_dict_headers(self):
        dict_headers = {"Header": "Header-Value"}
        rv = ("data", dict_headers)
        def_mime = "application/json"
        res = _parse_view_function_res(rv, Flask.response_class, def_mime)

        self.assertEqual(res[0], rv[0])
        self.assertEqual(res[1], 200)
        self.run_test_headers(res)

    def test_2_tuple_list_headers(self):
        # dict_headers = {"Header": "Header-Value"}
        list_headers = [("Header", "Header-Value")]
        # tuple_headers = (("Header", "Header-Value"),)
        # instance_headers = Headers(dict_headers)
        rv = ("data", list_headers)
        def_mime = "application/json"
        # rv, status, headers, mimetype
        res = _parse_view_function_res(rv, Flask.response_class, def_mime)

        self.assertEqual(res[0], rv[0])
        self.assertEqual(res[1], 200)
        self.run_test_headers(res)

    def test_2_tuple_tuple_headers(self):
        # dict_headers = {"Header": "Header-Value"}
        # list_headers = [("Header", "Header-Value")]
        tuple_headers = (("Header", "Header-Value"),)
        # instance_headers = Headers(dict_headers)
        rv = ("data", tuple_headers)
        def_mime = "application/json"
        # rv, status, headers, mimetype
        res = _parse_view_function_res(rv, Flask.response_class, def_mime)

        self.assertEqual(res[0], rv[0])
        self.assertEqual(res[1], 200)
        self.run_test_headers(res)

    def test_2_tuple_instance_headers(self):
        dict_headers = {"Header": "Header-Value"}
        # list_headers = [("Header", "Header-Value")]
        # tuple_headers = (("Header", "Header-Value"),)
        instance_headers = Headers(dict_headers)
        rv = ("data", instance_headers)
        def_mime = "application/json"
        # rv, status, headers, mimetype
        res = _parse_view_function_res(rv, Flask.response_class, def_mime)

        self.assertEqual(res[0], rv[0])
        self.assertEqual(res[1], 200)
        self.run_test_headers(res)
