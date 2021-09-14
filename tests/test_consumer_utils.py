from werkzeug.datastructures import Headers
from http import HTTPStatus
from ..open_spec.consumer._utils import (
    parse_status,
    parse_headers,
    resolve_oas_object,
)


def test_resolve_schema1():
    schema = {"type": "object", "properties": {"id": {"type": "string"}}}
    data = {
        "components": {},
        "paths": {"/gists": {"post": {"requestBody": {"schema": schema}}}},
    }
    assert (
        resolve_oas_object(
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
        resolve_oas_object(
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
    assert parse_status(404) == HTTPStatus.NOT_FOUND
    assert parse_status(500) == HTTPStatus.INTERNAL_SERVER_ERROR
    assert parse_status(408) == HTTPStatus.REQUEST_TIMEOUT


def test_parse_status_none():
    assert parse_status(None) == HTTPStatus.OK
    assert parse_status() == HTTPStatus.OK


def test_parse_status_statua():
    assert parse_status(HTTPStatus.OK) == HTTPStatus.OK
    assert (
        parse_status(HTTPStatus.INSUFFICIENT_STORAGE)
        == HTTPStatus.INSUFFICIENT_STORAGE
    )
    assert (
        parse_status(HTTPStatus.INTERNAL_SERVER_ERROR)
        == HTTPStatus.INTERNAL_SERVER_ERROR
    )
    assert (
        parse_status(HTTPStatus.REQUEST_TIMEOUT) == HTTPStatus.REQUEST_TIMEOUT
    )


def test_parse_headers_headers():
    headers = Headers()
    headers.add("Content_type", "application/json")

    assert parse_headers(headers) == headers
    assert parse_headers(headers).get("Content_type") == "application/json"


def test_parse_headers_tuple():
    _headers = (
        ("Content_type", "application/json"),
        ("Proxy-Connection", "Keep-Alive"),
    )
    expected = Headers(
        {"Content_type": "application/json", "Proxy-Connection": "Keep-Alive"}
    )

    assert parse_headers(_headers).get("Content_type") == expected.get(
        "Content_type"
    )
    assert parse_headers(_headers).get("Proxy-Connection") == expected.get(
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

    assert parse_headers(_headers).get("Content_type") == expected.get(
        "Content_type"
    )
    assert parse_headers(_headers).get("Proxy-Connection") == expected.get(
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

    assert parse_headers(_headers).get("Content_type") == expected.get(
        "Content_type"
    )
    assert parse_headers(_headers).get("Proxy-Connection") == expected.get(
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
        resolve_oas_object(
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
        resolve_oas_object(
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
        resolve_oas_object(
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
        resolve_oas_object(
            data,
            data.get("paths", {})
            .get("/gists", {})
            .get("post", {})
            .get("requestBody", {}),
            "rb",
        )
        == req
    )
