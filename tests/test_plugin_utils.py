from unittest import TestCase
from ..open_oasplugin import utils
from .schemas.schemas import GistSchema, gistObj1, get_schema


class TestPluginUtils(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_schema_class(self):
        schema = GistSchema
        info = utils.get_schema_info(schema)
        self.assertEqual(info["name"], "GistSchema")
        self.assertEqual(
            info["qualname"], "flask_open_oastests.schemas.schemas.GistSchema"
        )
        self.assertIsInstance(info["instance"], GistSchema)

    def test_schema_obj(self):
        schema = gistObj1
        info = utils.get_schema_info(schema)
        self.assertEqual(info["name"], "gistObj1")
        self.assertEqual(
            info["qualname"], "flask_open_oastests.schemas.schemas.gistObj1"
        )
        self.assertEqual(info["instance"], schema)

    def test_schema_func(self):
        schema = get_schema
        kwargs = {"type": "obj", "name": "gist1"}
        info = utils.get_schema_info(schema, **kwargs)
        self.assertEqual(info["name"], "get_schema")
        self.assertEqual(
            info["qualname"], "flask_open_oastests.schemas.schemas.get_schema"
        )
        self.assertEqual(info["kwargs"], kwargs)
        self.assertIsInstance(info["instance"], GistSchema)

    def test_schema_func2(self):
        schema = get_schema
        kwargs = {"type": "class", "name": "gist"}
        info = utils.get_schema_info(schema, **kwargs)
        self.assertEqual(info["name"], "get_schema")
        self.assertEqual(
            info["qualname"], "flask_open_oastests.schemas.schemas.get_schema"
        )
        self.assertEqual(info["kwargs"], kwargs)

        self.assertEqual(info["instance"], GistSchema)

    def test_schema_str(self):
        schema = "flask_open_oastests.schemas.schemas.GistSchema"
        info = utils.get_schema_info(schema)
        self.assertEqual(info["name"], "GistSchema")
        self.assertEqual(
            info["qualname"], "flask_open_oastests.schemas.schemas.GistSchema"
        )
        self.assertIsInstance(info["instance"], GistSchema)

    def test_schema_str2(self):
        schema = "flask_open_oastests.schemas.schemas.gistObj1"
        info = utils.get_schema_info(schema)
        self.assertEqual(info["name"], "gistObj1")
        self.assertEqual(
            info["qualname"], "flask_open_oastests.schemas.schemas.gistObj1"
        )
        self.assertEqual(info["instance"], gistObj1)

    def test_schema_str3(self):
        schema = "flask_open_oastests.schemas.schemas.get_schema"
        kwargs = {"type": "class", "name": "gist"}

        info = utils.get_schema_info(schema, **kwargs)
        self.assertEqual(info["name"], "get_schema")
        self.assertEqual(
            info["qualname"], "flask_open_oastests.schemas.schemas.get_schema"
        )
        self.assertEqual(info["kwargs"], kwargs)

        self.assertEqual(info["instance"], GistSchema)

    def test_schema_str4(self):
        schema = "GistSchema"
        info = utils.get_schema_info(schema)
        self.assertEqual(info["name"], "GistSchema")
        self.assertEqual(
            info["qualname"], "flask_open_oastests.schemas.schemas.GistSchema"
        )
        self.assertIsInstance(info["instance"], GistSchema)
