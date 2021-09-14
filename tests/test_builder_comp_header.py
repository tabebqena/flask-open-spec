from ..open_spec.builder.builder import OasBuilder
from unittest import TestCase
from ..tests.schemas.schemas import (
    gistObj1
)
from ..open_spec.decorators import Deferred, component_header


class TestComponentHeader(TestCase):
    def run_tests(self, builder: OasBuilder):
        obj_qualname = "flask_open_spec.tests.schemas.schemas.gistObj1"
        data = builder.get_data()

        header = (
            data.get("components", {})
            .get("headers", {})
            .get("X-Request-ID", None)
        )
        self.assertIsNotNone(header)
        self.assertIn("schema", header)

        self.assertEqual(
            header.get("schema", {}).get("$ref", None),
            "#/components/schemas/Gist",
        )
        self.assertEqual(header.get("x-schema", {}), obj_qualname)

        schemas = data.get("components", {}).get("schemas", {})
        self.assertEqual(schemas.get("Gist", {}).get("x-schema"), obj_qualname)

    def test_data(self):
        data = {
            "components": {
                "headers": {
                    "X-Request-ID": {
                        "description": "The number of allowed requests in the current period",
                        "schema": gistObj1,
                        "required": False,
                    },
                }
            },
        }

        builder = OasBuilder(data)
        self.run_tests(builder)

    def test_data_dict(self):
        data = {
            "components": {
                "headers": {
                    "X-Request-ID": {
                        "description": "The number of allowed requests in the current period",
                        "schema": {"type": "object"},
                        "required": False,
                    },
                }
            },
        }

        builder = OasBuilder(data)
        # pprint.pprint(builder.get_data())
        self.assertEqual(
            builder.get_data().get("components", {}).get("headers", {}),
            data.get("components", {}).get("headers", {}),
        )
        # self.run_tests(builder)

    def test_decorator(self):
        component_header("X-Request-ID", gistObj1, description=gistObj1)

        builder = OasBuilder()
        self.run_tests(builder)

    def tearDown(self) -> None:
        Deferred._deferred = []
        return super().tearDown()
