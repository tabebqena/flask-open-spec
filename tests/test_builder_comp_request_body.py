from ..open_spec.builder.builder import OasBuilder
from unittest import TestCase
from ..tests.schemas.schemas import (
    GistSchema
)
from ..open_spec.decorators import Deferred, component_request_body


class TestComponentRequestBodies(TestCase):
    def run_tests(self, builder: OasBuilder):
        klass_qualname = "flask_open_spec.tests.schemas.schemas.GistSchema"
        data = builder.get_data()
        #
        bodies = data.get("components", {}).get("requestBodies", {})
        self.assertIn("GistBody", bodies)

        self.assertEqual(
            bodies["GistBody"]["content"]["application/json"]["schema"]["$ref"],
            "#/components/schemas/Gist",
        )

        self.assertEqual(
            bodies.get("GistBody", {})
            .get("content", {})
            .get("application/json", {})
            .get(
                "x-schema",
            ),
            klass_qualname,
        )
        schemas = data.get("components", {}).get("schemas", {})
        self.assertEqual(
            schemas.get("Gist", {}).get("x-schema"), klass_qualname
        )

    def test_data(self):
        data = {
            "components": {
                "requestBodies": {
                    "GistBody": {
                        "description": "A JSON object containing gist information",
                        "required": True,
                        "content": {"application/json": {"schema": GistSchema}},
                    }
                }
            }
        }

        builder = OasBuilder(data)
        # pprint(builder.get_data())
        self.run_tests(builder)

    def test_data_dict_schema(self):
        data = {
            "components": {
                "requestBodies": {
                    "GistBody": {
                        "description": "A JSON object containing gist information",
                        "required": True,
                        "content": {
                            "application/json": {"schema": {"type": "object"}}
                        },
                    }
                }
            }
        }

        builder = OasBuilder(data)
        self.assertEqual(
            builder.get_data().get("components", {}).get("requestBodies", {}),
            data.get("components", {}).get("requestBodies", {}),
        )
        # self.run_tests(builder)

    def test_data_none_schema(self):
        data = {
            "components": {
                "requestBodies": {
                    "GistBody2": {
                        "description": "A JSON object containing gist information",
                        "required": True,
                        "content": {"application/json": {"schema": None}},
                    }
                }
            }
        }

        builder = OasBuilder(data)
        self.assertEqual(
            builder.get_data().get("components", {}).get("requestBodies", {}),
            {
                "GistBody2": {
                    "description": "A JSON object containing gist information",
                    "required": True,
                    "content": {"application/json": {"schema": {}}},
                }
            },
        )
        # self.run_tests(builder)

    def test_decorator(self):
        component_request_body("GistBody", "application/json", GistSchema)

        builder = OasBuilder()
        self.run_tests(builder)

    def tearDown(self) -> None:
        Deferred._deferred = []
        return super().tearDown()
