from ..open_oas.builder.builder import OasBuilder
from unittest import TestCase
from ..tests.schemas.schemas import GistSchema, gistObj1
from ..open_oas.decorators import Deferred, path_request_body


class TestPathRequestBody(TestCase):
    def run_tests(self, builder: OasBuilder):
        data = builder.get_data()
        content = (
            data.get("paths", {})
            .get("/gists", {})
            .get("post", {})
            .get("requestBody", {})
            .get("content", {})
        )
        self.assertNotEqual(content, {})
        for _, val in content.items():
            self.assertEqual(
                val.get("schema", {}).get("$ref", {}),
                "#/components/schemas/Gist",
            )
            self.assertEqual(
                val.get("x-schema", {}),
                "flask_open_oas.tests.schemas.schemas.gistObj1",
            )

    def run_tests2(self, builder: OasBuilder):
        data = builder.get_data()
        content = (
            data.get("paths", {})
            .get("/gists", {})
            .get("post", {})
            .get("requestBody", {})
            .get("content", {})
        )
        self.assertNotEqual(content, {})

        for _, val in content.items():
            self.assertEqual(
                val.get("schema", {}).get("$ref", {}),
                "#/components/schemas/Gist1",
            )
            self.assertEqual(
                val.get("x-schema", {}),
                "flask_open_oas.tests.schemas.schemas.gistObj1",
            )

    def test_data(self):
        data = {
            "paths": {
                "/gists": {
                    "post": {
                        "requestBody": {
                            # "description": "Optional description in *Markdown*",
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": gistObj1,
                                },
                                "application/xml": {
                                    "schema": gistObj1,
                                },
                                "application/x-www-form-urlencoded": {
                                    "schema": gistObj1,
                                },
                            },
                        },
                    }
                },
            },
        }

        builder = OasBuilder(data)
        # pprint(builder.get_data())
        self.run_tests(builder)

    def test_data_dict_schema(self):
        data = {
            "paths": {
                "/gists": {
                    "post": {
                        "requestBody": {
                            # "description": "Optional description in *Markdown*",
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"},
                                },
                                "application/xml": {
                                    "schema": {"type": "object"},
                                },
                                "application/x-www-form-urlencoded": {
                                    "schema": {"type": "object"},
                                },
                            },
                        },
                    }
                },
            },
        }

        builder = OasBuilder(data)
        self.assertEqual(
            builder.get_data()
            .get("paths", {})
            .get("/gists", {})
            .get("post", {})
            .get("requestBody", {})
            .get("required"),
            data.get("paths", {})
            .get("/gists", {})
            .get("post", {})
            .get("requestBody", {})
            .get("required"),
        )
        self.assertEqual(
            builder.get_data()
            .get("paths", {})
            .get("/gists", {})
            .get("post", {})
            .get("requestBody", {})
            .get("content", {})
            .get("application/json", {}),
            data.get("paths", {})
            .get("/gists", {})
            .get("post", {})
            .get("requestBody", {})
            .get("content", {})
            .get("application/json", {}),
        )
        self.assertEqual(
            builder.get_data()
            .get("paths", {})
            .get("/gists", {})
            .get("post", {})
            .get("requestBody", {})
            .get("content", {})
            .get("application/xml", {}),
            data.get("paths", {})
            .get("/gists", {})
            .get("post", {})
            .get("requestBody", {})
            .get("content", {})
            .get("application/xml", {}),
        )
        self.assertEqual(
            builder.get_data()
            .get("paths", {})
            .get("/gists", {})
            .get("post", {})
            .get("requestBody", {})
            .get("content", {})
            .get("application/x-www-form-urlencoded", {}),
            data.get("paths", {})
            .get("/gists", {})
            .get("post", {})
            .get("requestBody", {})
            .get("content", {})
            .get("application/x-www-form-urlencoded", {}),
        )
        # self.run_tests(builder)

    def test_data2(self):
        data = {
            "components": {
                "schemas": {
                    "Gist": GistSchema,
                },
            },
            "paths": {
                "/gists": {
                    "post": {
                        "requestBody": {
                            # "description": "Optional description in *Markdown*",
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": gistObj1,
                                },
                                "application/xml": {
                                    "schema": gistObj1,
                                },
                                "application/x-www-form-urlencoded": {
                                    "schema": gistObj1,
                                },
                            },
                        },
                    }
                },
            },
        }

        builder = OasBuilder(data)
        self.run_tests2(builder)

    def test_decorator(self):

        path_request_body(
            gistObj1,
            ["/gists"],
            ["post"],
            [
                "application/json",
                "application/xml",
                "application/x-www-form-urlencoded",
            ],
            required=True,
        )

        builder = OasBuilder()
        self.run_tests(builder)

    def test_decorator2(self):
        data = {
            "components": {
                "schemas": {
                    "Gist": GistSchema,
                },
            },
        }
        path_request_body(
            gistObj1,
            ["/gists"],
            ["post"],
            [
                "application/json",
                "application/xml",
                "application/x-www-form-urlencoded",
            ],
            required=True,
        )

        builder = OasBuilder(data)
        self.run_tests2(builder)

    def tearDown(self) -> None:
        Deferred._deferred = []
        return super().tearDown()
