from pprint import pprint
from ..open_spec.builder.builder import OasBuilder
from unittest import TestCase
from ..tests.schemas.schemas import (
    ErrorSchema,
    GistSchema,
    gistObj1,
)
from ..open_spec.decorators import Deferred, path_details


class TestPathDetails(TestCase):
    def run_tests(self, builder: OasBuilder):
        path_data = builder.get_data().get("paths", {}).get("/gists", {})
        self.assertNotEqual(path_data, {})
        self.assertEqual(
            path_data.get("summary", ""), self.data.get("summary", "-")
        )
        self.assertEqual(
            path_data.get("description", ""), self.data.get("description", "-")
        )
        self.assertEqual(
            path_data.get("servers", []), self.data.get("servers", [""])
        )

    def setUp(self) -> None:
        self.data = {
            "summary": "add gist",
            "description": "add gist to the gists list, return json representation of the added gist",
            "servers": [
                "production.127.0.0.1/",
                "testing.127.0.0.1/",
            ],
        }
        return super().setUp()

    def test_data(self):

        _data = {
            "paths": {"/gists": self.data},
        }

        builder = OasBuilder(_data)
        self.run_tests(builder)

    def test_decorator(self):

        path_details(
            ["/gists"],
            summary=self.data.get("summary"),
            description=self.data.get("description"),
            servers=self.data.get("servers"),
        )

        builder = OasBuilder()
        self.run_tests(builder)

    def tearDown(self) -> None:
        Deferred._deferred = []
        return super().tearDown()
