from ..open_spec.builder.builder import OasBuilder
from unittest import TestCase
from .schemas.schemas import GistSchema, gistObj1, get_schema
from ..open_spec.decorators import Deferred, component_schema


class TestSchemaDict(TestCase):
    def test_at_runtime(self):
        data = {
            "components": {
                "schemas": {
                    "Gist": {"type": "object"},
                },
            },
        }
        builder = OasBuilder(data)
        self.assertEqual(
            data.get("components", {}).get("schemas", {}),
            builder.get_data().get("components", {}).get("schemas", {}),
        )


class TestSchemaKlass(TestCase):
    def setUp(self) -> None:
        self.schema_instance = GistSchema
        self.schema_name = "GistSchema"
        self.schema_qualname = (
            "flask_open_spec.tests.schemas.schemas.GistSchema"
        )

        return super().setUp()

    def usual_check(self, builder):
        data = builder.get_data()
        gisty = data.get("components", {}).get("schemas", {}).get("Gist", {})
        # print("gisty:", gisty)
        self.assertIsNotNone(gisty)
        self.assertIn("x-schema", gisty)

    def test_at_runtime(self):
        data = {
            "components": {"schemas": {"Gist": self.schema_instance}},
        }
        builder = OasBuilder(data)
        self.usual_check(builder)

    def test_by_name(self):
        data = {
            "components": {"schemas": {"Gist": self.schema_name}},
        }
        builder = OasBuilder(data)
        self.usual_check(builder)

    def test_by_qualname(self):
        data = {
            "components": {"schemas": {"Gist": self.schema_qualname}},
        }
        builder = OasBuilder(data)
        self.usual_check(builder)

    def test_with_args(self):
        data = {
            "components": {
                "schemas": {"Gist": self.schema_qualname},
                "schemas-kwargs": {"Gist": {"only": ["id", "name"]}},
            },
        }
        builder = OasBuilder(data)
        self.usual_check(builder)
        data = builder.get_data()
        gisty = data.get("components", {}).get("schemas", {}).get("Gist", {})
        self.assertEqual(len(gisty.get("properties", {})), 2)

    def tearDown(self) -> None:
        Deferred._deferred = []
        return super().tearDown()


class TestSchemaObj(TestSchemaKlass):
    def setUp(self) -> None:
        self.schema_instance = gistObj1
        # self.schema_name = "GistSchema"
        self.schema_qualname = "flask_open_spec.tests.schemas.schemas.gistObj1"

        return super().setUp()

    def test_by_name(self):
        return

    def test_at_runtime(self):
        data = {
            "components": {"schemas": {"Gist": self.schema_instance}},
        }
        builder = OasBuilder(data)
        self.usual_check(builder)

    def test_by_qualname(self):
        data = {
            "components": {"schemas": {"Gist": self.schema_qualname}},
        }
        builder = OasBuilder(data)
        self.usual_check(builder)

    def test_with_args(self):
        return

    def tearDown(self) -> None:
        Deferred._deferred = []

        return super().tearDown()


class TestSchemaFactory(TestSchemaKlass):
    def setUp(self) -> None:
        self.schema_qualname = (
            "flask_open_spec.tests.schemas.schemas.get_schema"
        )
        self.schema_instance = get_schema

        return super().setUp()

    def test_at_runtime(self):
        return

    def test_by_name(self):
        return

    def test_by_qualname(self):
        return

    def test_with_args_instance(self):
        data = {
            "components": {
                "schemas": {"Gist": self.schema_instance},
                "schemas-kwargs": {"type": "class", "name": "gist"},
            },
        }
        builder = OasBuilder(data)
        self.usual_check(builder)
        data = builder.get_data()
        gisty = data.get("components", {}).get("schemas", {}).get("Gist", {})

        self.assertEqual(len(gisty.get("properties", {})), 5)

    def test_with_args_qual(self):
        data = {
            "components": {
                "schemas": {"Gist": self.schema_qualname},
                "schemas-kwargs": {"type": "class", "name": "gist"},
            },
        }
        builder = OasBuilder(data)
        self.usual_check(builder)
        data = builder.get_data()
        gisty = data.get("components", {}).get("schemas", {}).get("Gist", {})

        self.assertEqual(len(gisty.get("properties", {})), 5)


class TestSchemaKlassDecorator(TestSchemaKlass):
    def test_at_runtime(self):
        component_schema(self.schema_instance)
        builder = OasBuilder()
        self.usual_check(builder)

    def test_by_name(self):
        component_schema(self.schema_name)
        builder = OasBuilder()
        self.usual_check(builder)

    def test_by_qualname(self):
        component_schema(self.schema_qualname)
        builder = OasBuilder()
        self.usual_check(builder)

    def test_with_args(self):
        component_schema(self.schema_name, {"only": ["id", "name"]})
        builder = OasBuilder()

        data = builder.get_data()
        gist = data.get("components", {}).get("schemas", {}).get("Gist", {})

        self.assertEqual(len(gist.get("properties", {})), 2)
        self.usual_check(builder)

    def tearDown(self) -> None:
        Deferred._deferred = []
        return super().tearDown()


class TestSchemaObjDecorator(TestSchemaObj):
    def test_by_name(self):
        return

    def test_at_runtime(self):
        component_schema(self.schema_instance)
        builder = OasBuilder()
        self.usual_check(builder)

    def test_by_qualname(self):
        component_schema(self.schema_qualname)
        builder = OasBuilder()
        self.usual_check(builder)

    def test_with_args(self):
        return

    def tearDown(self) -> None:
        return super().tearDown()


class TestSchemaFactoryDecorator(TestSchemaFactory):
    def test_at_runtime(self):
        return

    def test_by_name(self):
        return

    def test_by_qualname(self):
        return

    def test_with_args(self):
        component_schema(self.schema_qualname)
        builder = OasBuilder()
        self.usual_check(builder)
        data = builder.get_data()
        gisty = data.get("components", {}).get("schemas", {}).get("Gist", {})

        self.assertEqual(len(gisty.get("properties", {})), 5)
