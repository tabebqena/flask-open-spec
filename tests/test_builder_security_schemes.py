from ..open_oas.builder.builder import OasBuilder
from unittest import TestCase
from ..open_oas.decorators import (
    Deferred,
    api_key_security_schema,
    api_basic_security_scheme,
    api_bearer_security_scheme,
)


class TestData(TestCase):
    basic_auth_data = {
        "components": {
            "securitySchemes": {
                "basicAuth": {"type": "http", "scheme": "basic"}
            }
        }
    }
    bearer_auth_data = {
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                },
            }
        }
    }
    api_key_auth_data = {
        "components": {
            "securitySchemes": {
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-KEY",
                },
            }
        }
    }

    def test_basic_auth(self):
        self.builder = OasBuilder(
            self.basic_auth_data,
        )
        data = self.builder.get_data()
        self.assertEqual(
            data.get("components", {}).get("securitySchemes"),
            self.basic_auth_data.get("components", {}).get("securitySchemes"),
        )

    def test_basic_auth_decorator(self):
        api_basic_security_scheme("basicAuth")
        self.builder = OasBuilder()
        data = self.builder.get_data()
        self.assertEqual(
            data.get("components", {}).get("securitySchemes"),
            self.basic_auth_data.get("components", {}).get("securitySchemes"),
        )

    def test_bearer_auth(self):
        self.builder = OasBuilder(
            self.bearer_auth_data,
        )
        data = self.builder.get_data()
        self.assertEqual(
            data.get("components", {}).get("securitySchemes"),
            self.bearer_auth_data.get("components", {}).get("securitySchemes"),
        )

    def test_bearer_auth_decorator(self):
        api_bearer_security_scheme("bearerAuth", bearer_format="JWT")
        self.builder = OasBuilder()
        data = self.builder.get_data()
        self.assertEqual(
            data.get("components", {}).get("securitySchemes"),
            self.bearer_auth_data.get("components", {}).get("securitySchemes"),
        )

    def test_api_key_auth(self):
        self.builder = OasBuilder(
            self.api_key_auth_data,
        )
        data = self.builder.get_data()
        self.assertEqual(
            data.get("components", {}).get("securitySchemes"),
            self.api_key_auth_data.get("components", {}).get("securitySchemes"),
        )

    def test_api_key_auth_decorator(self):
        api_key_security_schema(
            "ApiKeyAuth", in_="header", location_name="X-API-KEY"
        )
        self.builder = OasBuilder()
        data = self.builder.get_data()
        self.assertEqual(
            data.get("components", {}).get("securitySchemes"),
            self.api_key_auth_data.get("components", {}).get("securitySchemes"),
        )

    def tearDown(self) -> None:
        Deferred._deferred = []
        return super().tearDown()
