from ..open_oas.open_oas.builder.builder import OasBuilder
from unittest import TestCase
from ..tests.schemas.schemas import PaginationSchema
from ..open_oas.open_oas.decorators import component_parameter, Deferred


class TestComponentParameter(TestCase):
    def run_tests(self, builder: OasBuilder):
        klass_qualname = "flask_open_oas.tests.schemas.schemas.PaginationSchema"
        data = builder.get_data()
        schemas = data.get("components", {}).get("schemas", {})
        parameters = data.get("components", {}).get("parameters", {})
        self.assertEqual(
            schemas.get("Pagination", {}).get("x-schema", ""), klass_qualname
        )
        self.assertIn("offsetParam", parameters)
        self.assertIn("limitParam", parameters)

    def test_dict_schema(self):
        data = {
            "components": {
                "parameters": {
                    "offsetParam": {
                        "schema": {
                            "type": "integer",
                        },
                        "in": "query",
                        "name": "offsetParam",
                        "required": False,
                        "description": "",
                    },
                    "limitParam": {
                        "schema": {
                            "type": "integer",
                        },
                        "in": "query",
                        "name": "limitParam",
                        "required": False,
                        "description": "",
                    },
                },
            }
        }
        builder = OasBuilder(data)

        self.assertEqual(
            builder.get_data().get("components").get("parameters"),
            data.get("components").get("parameters"),
        )

        # pprint.pprint(builder.get_data())
        # self.run_tests(builder)

    def test_data(self):
        data = {
            "components": {
                "parameters": {
                    "offsetParam": {
                        "schema": PaginationSchema,
                        "in": "query",
                        "name": "offsetParam",
                        "required": False,
                    },
                    "limitParam": {
                        "schema": PaginationSchema,
                        "in": "query",
                        "name": "limitParam",
                        "required": False,
                    },
                },
            },
            "paths": {
                "/users": {
                    "get": {
                        "summary": "Gets a list of users.",
                        # "parameters": [],
                        "responses": {"200": {"description": "OK"}},
                    }
                }
            },
        }

        builder = OasBuilder(data)
        # pprint.pprint(builder.get_data())
        self.run_tests(builder)

    def test_decorator(self):
        component_parameter(
            "offsetParam",
            in_="query",
            name="offsetParam",
            schema=PaginationSchema,
        )
        component_parameter(
            "limitParam",
            in_="query",
            name="limitParam",
            schema=PaginationSchema,
        )
        builder = OasBuilder()
        self.run_tests(builder)

    def tearDown(self) -> None:
        Deferred._deferred = []

        return super().tearDown()
