from ..open_oas.builder.builder import OasBuilder
from unittest import TestCase
from ..tests.schemas.schemas import PaginationSchema
from ..open_oas.decorators import Deferred, path_parameter


class TestPathParameter(TestCase):
    def run_tests(self, builder: OasBuilder):
        data = builder.get_data()
        parameters = (
            data.get("paths", {}).get("/gists", {})
            # .get("get", {})
            .get("parameters", [])
        )
        self.assertNotEqual(parameters, [])
        for param in parameters:
            self.assertEqual(
                param.get("schema", {}).get("$ref", {}),
                "#/components/schemas/Pagination",
            )

    def test_data(self):
        data = {
            "paths": {
                "/gists": {
                    "parameters": [
                        {
                            "schema": PaginationSchema,
                            "in": "query",
                            "name": "offsetParam",
                            "required": False,
                        },
                        {
                            "schema": PaginationSchema,
                            "in": "query",
                            "name": "limitParam",
                            "required": False,
                        },
                    ],
                    "get": {
                        "summary": "Gets a list of users.",
                        "responses": {"200": {"description": "OK"}},
                    },
                }
            },
        }

        builder = OasBuilder(data)
        # pprint(builder.get_data())
        self.run_tests(builder)

    def test_data_dict_schema(self):
        data = {
            "paths": {
                "/gists": {
                    "parameters": [
                        {
                            "schema": {"type": "object"},
                            "in": "query",
                            "name": "offsetParam",
                            "required": False,
                        },
                        {
                            "schema": {"type": "object"},
                            "in": "query",
                            "name": "limitParam",
                            "required": False,
                        },
                    ],
                    "get": {
                        "summary": "Gets a list of users.",
                        "responses": {"200": {"description": "OK"}},
                    },
                }
            },
        }

        builder = OasBuilder(data)
        # pprint(builder.get_data())
        # self.run_tests(builder)
        parameters = (
            builder.get_data()
            .get("paths", {})
            .get("/gists", {})
            # .get("get", {})
            .get("parameters", [])
        )
        self.assertEqual(
            parameters,
            data.get("paths", {}).get("/gists", {})
            # .get("get", {})
            .get("parameters", []),
        )

    def test_decorator(self):
        path_parameter(
            ["/gists"],
            "query",
            name="offsetParam",
            schema=PaginationSchema,
            description="",
        )
        path_parameter(
            ["/gists"],
            "query",
            name="limitParam",
            schema=PaginationSchema,
            description="",
        )

        builder = OasBuilder()
        # pprint(builder.get_data())
        self.run_tests(builder)

    def tearDown(self) -> None:
        Deferred._deferred = []
        return super().tearDown()
