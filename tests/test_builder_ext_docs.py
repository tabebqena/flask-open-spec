from ..open_oas.builder.builder import OasBuilder
from unittest import TestCase
from ..open_oas.decorators import Deferred, api_external_docs


class TestExtDocs(TestCase):
    def _data(self):
        self.data = {
            "externalDocs": {
                "url": "externalDocs url",
                "description": "externalDocs description",
            }
        }

    def setUp(self) -> None:
        self._data()
        self.builder = OasBuilder(
            self.data,
        )
        return super().setUp()

    def test_info_from_data(self):
        data = self.builder.get_data()
        self.assertEqual(
            data.get("externalDocs"), self.data.get("externalDocs")
        )

    def tearDown(self) -> None:
        return super().tearDown()


class TestDeferred(TestCase):
    def _data(self):
        self.data = {
            "externalDocs": {
                "url": "externalDocs url",
                "description": "externalDocs description",
            }
        }

    def set_deferred(self):
        self.deferred_data = {
            "externalDocs": {
                "url": "new externalDocs url",
                "description": "new externalDocs description",
            }
        }
        Deferred._deferred = [
            (
                "api_external_docs",
                (),
                {
                    "url": self.deferred_data.get("externalDocs", {}).get(
                        "url"
                    ),
                    "description": self.deferred_data.get(
                        "externalDocs", {}
                    ).get("description"),
                },
            )
        ]

    def setUp(self) -> None:
        self._data()
        self.set_deferred()
        self.builder = OasBuilder(self.data)
        return super().setUp()

    def test_from_deferred(self):
        data = self.builder.get_data()
        self.assertEqual(
            data.get("externalDocs"), self.deferred_data.get("externalDocs")
        )

    def tearDown(self) -> None:
        Deferred._deferred = []

        return super().tearDown()


class TestDecorator(TestCase):
    def setUp(self) -> None:
        self.data = {
            "url": "externalDocs url",
            "description": "externalDocs description",
        }
        api_external_docs(**self.data)
        self.builder = OasBuilder()
        return super().setUp()

    def test_decorator(self):
        data = self.builder.get_data()
        self.assertEqual(data.get("externalDocs"), self.data)

    def tearDown(self) -> None:
        Deferred._deferred = []

        return super().tearDown()
