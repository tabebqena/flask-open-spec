from ..open_spec.decorators import Deferred, api_tag
from ..open_spec.builder.builder import OasBuilder
from unittest import TestCase


class TestTags(TestCase):
    def _data(self):
        self.tags = [
            {
                "name": "tag1",
                "description": "tag1 description",
                "externalDocs": {"url": "tag1 url"},
            },
            {
                "name": "tag2",
                "description": "tag2 description",
                "externalDocs": {"url": "tag2 url"},
            },
            {
                "name": "tag3",
                "description": "tag3 description",
                "externalDocs": {"url": "tag3 url"},
            },
        ]
        return {"tags": self.tags}

    def setUp(self) -> None:

        self.builder = OasBuilder(self._data())
        return super().setUp()

    def test_tags_from_data(self):
        data = self.builder.get_data().get("tags", [])
        self.assertEqual(len(data), len(self.tags))
        for t in self.tags:
            self.assertIn(t, data)
        # self.assertEqual(data.get("tags"), self.tags)

    def tearDown(self) -> None:
        Deferred._deferred = []

        return super().tearDown()


class TestDeferred(TestCase):
    def _data(self):

        return {
            "tags": [
                {
                    "name": "tag1",
                    "description": "tag1 description",
                    "externalDocs": {"url": "tag1 url"},
                },
                {
                    "name": "tag2",
                    "description": "tag2 description",
                    "externalDocs": {"url": "tag2 url"},
                },
                {
                    "name": "tag3",
                    "description": "tag3 description",
                    "externalDocs": {"url": "tag3 url"},
                },
            ]
        }

    def set_deferred(self):
        self.tags = [
            {
                "name": "tag1",
                "description": "new tag1 description",
                "externalDocs": {"url": "new tag1 url"},
            },
            {
                "name": "tag2",
                "description": "new tag2 description",
                "externalDocs": {"url": "new tag2 url"},
            },
            {
                "name": "tag3",
                "description": "new tag3 description",
                "externalDocs": {"url": "new tag3 url"},
            },
        ]

        for tag in self.tags:
            Deferred._deferred.append(
                (
                    "api_tag",
                    (
                        tag["name"],
                        tag["description"],
                        tag["externalDocs"]["url"],
                    ),
                    {
                        # "external_docs_url": tag["externalDocs"]["url"],
                        # "description": tag["description"],
                    },
                )
            )

    def setUp(self) -> None:
        self._data()
        self.set_deferred()
        self.builder = OasBuilder(self._data())
        return super().setUp()

    def test_from_deferred(self):
        data = self.builder.get_data().get("tags", [])

        """for tag in data:
            input_tag = {}
            for t in self.tags:
                if t["name"] == tag["name"]:
                    input_tag = t
            self.assertEqual(tag, input_tag)"""
        data = self.builder.get_data().get("tags", [])
        # self.assertEqual(len(data), 3)
        for t in self.tags:
            self.assertIn(t, data)

    def tearDown(self) -> None:
        Deferred._deferred = []

        return super().tearDown()


class TestDecorator(TestCase):
    def setUp(self) -> None:
        self.tags = [
            {
                "name": "tag1",
                "description": "new tag1 description",
                "externalDocs": {"url": "new tag1 url"},
            },
            {
                "name": "tag2",
                "description": "new tag2 description",
                "externalDocs": {"url": "new tag2 url"},
            },
            {
                "name": "tag3",
                "description": "new tag3 description",
                "externalDocs": {"url": "new tag3 url"},
            },
        ]

        for t in self.tags:
            api_tag(
                name=t["name"],
                description=t["description"],
                external_docs_url=t["externalDocs"]["url"],
            )
        self.builder = OasBuilder()
        return super().setUp()

    def test_decorator(self):
        data = self.builder.get_data()
        self.assertEqual(data.get("tags", []), self.tags)

    def tearDown(self) -> None:
        Deferred._deferred = []

        return super().tearDown()
