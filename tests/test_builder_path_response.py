from ..open_spec.builder.builder import OasBuilder
from unittest import TestCase
from ..tests.schemas.schemas import (
    GistSchema,
    gistObj1
)
from ..open_spec.decorators import Deferred, path_response


class TestPathResponse(TestCase):
    def run_tests(self, builder: OasBuilder):
        data = builder.get_data()
        content = (
            data.get("paths", {})
            .get("/gists", {})
            .get("post", {})
            .get("responses", {})
            .get("200", {})
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
                "flask_open_spec.tests.schemas.schemas.gistObj1",
            )

    def run_tests2(self, builder: OasBuilder):
        data = builder.get_data()
        content = (
            data.get("paths", {})
            .get("/gists", {})
            .get("post", {})
            .get("responses", {})
            .get("200", {})
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
                "flask_open_spec.tests.schemas.schemas.gistObj1",
            )

    def test_data(self):
        data = {
            "paths": {
                "/gists": {
                    "post": {
                        "responses": {
                            "200": {
                                "description": "OK",
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
                            }
                        },
                    },
                },
            },
        }

        builder = OasBuilder(data)
        self.run_tests(builder)

    def test_data_dict_schema(self):
        data = {
            "paths": {
                "/gists": {
                    "post": {
                        "responses": {
                            "200": {
                                "description": "OK",
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
                            }
                        },
                    },
                },
            },
        }

        builder = OasBuilder(data)
        self.assertEqual(
            builder.get_data()
            .get("paths", {})
            .get("/gists", {})
            .get("responses", {}),
            data.get("paths", {}).get("/gists", {}).get("responses", {}),
        )
        # pprint(builder.get_data())
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
                        "responses": {
                            "200": {
                                "description": "OK",
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
                            }
                        },
                    },
                },
            },
        }

        builder = OasBuilder(data)
        self.run_tests2(builder)

    def test_decorator(self):

        path_response(
            gistObj1,
            ["/gists"],
            ["post"],
            codes=["200"],
            content_types=[
                "application/json",
                "application/xml",
                "application/x-www-form-urlencoded",
            ],
            description="OK",
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
        path_response(
            gistObj1,
            ["/gists"],
            ["post"],
            codes=["200"],
            content_types=[
                "application/json",
                "application/xml",
                "application/x-www-form-urlencoded",
            ],
            description="OK",
        )

        builder = OasBuilder(data)
        self.run_tests2(builder)

    def tearDown(self) -> None:
        Deferred._deferred = []
        return super().tearDown()
