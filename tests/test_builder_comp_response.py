from ..open_oas.builder.builder import OasBuilder
from unittest import TestCase
from ..tests.schemas.schemas import (
    ErrorSchema,
    GistSchema,
    gistObj1,
)
from ..open_oas.decorators import Deferred, component_response


class TestComponentResponse(TestCase):
    def run_tests(self, builder: OasBuilder):
        klass_qualname = "flask_open_oas.tests.schemas.schemas.GistSchema"
        obj_qualname = "flask_open_oas.tests.schemas.schemas.gistObj1"
        error_qualname = "flask_open_oas.tests.schemas.schemas.ErrorSchema"
        data = builder.get_data()

        responses = data.get("components", {}).get("responses", {})
        _map = {
            "404": "Error",
            "ok_response": "Gist",
            "ok2_response": "Gist1",
        }
        for k in responses.keys():
            self.assertEqual(
                responses[k]["content"]["application/json"]["schema"]["$ref"],
                f"#/components/schemas/{_map[k]}",
            )

        schemas = data.get("components", {}).get("schemas", {})
        self.assertEqual(
            schemas.get("Error", {}).get("x-schema"), error_qualname
        )
        self.assertEqual(schemas.get("Gist", {}).get("x-schema"), obj_qualname)
        self.assertEqual(
            schemas.get("Gist1", {}).get("x-schema"), klass_qualname
        )

    def test_data(self):
        data = {
            "components": {
                "responses": {
                    "ok_response": {
                        "content": {
                            "application/json": {"schema": gistObj1},
                        },
                        "description": "",
                    },
                    "ok2_response": {
                        "content": {
                            "application/json": {"schema": GistSchema},
                        },
                        "description": "",
                    },
                    "404": {
                        "content": {
                            "application/json": {"schema": ErrorSchema},
                        },
                        "description": "",
                    },
                },
            },
        }

        builder = OasBuilder(data)
        self.run_tests(builder)

    def test_data_dict_schema(self):
        data = {
            "components": {
                "responses": {
                    "ok_response": {
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"},
                            },
                        },
                        "description": "",
                    },
                    "ok2_response": {
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"},
                            },
                        },
                        "description": "",
                    },
                    "404": {
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"},
                            },
                        },
                        "description": "",
                    },
                },
            },
        }

        builder = OasBuilder(data)
        self.assertEqual(
            builder.get_data().get("components"), data.get("components")
        )
        # pprint.pprint(builder.get_data())
        # self.run_tests(builder)

    def test_decorator(self):
        component_response("ok_response", "application/json", gistObj1)
        component_response("ok2_response", "application/json", GistSchema)
        component_response("404", "application/json", ErrorSchema)

        builder = OasBuilder()
        self.run_tests(builder)

    def tearDown(self) -> None:
        Deferred._deferred = []
        return super().tearDown()
