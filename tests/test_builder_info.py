from ..open_oas.builder.builder import OasBuilder
from unittest import TestCase
from ..open_oas.decorators import api_info, Deferred


class TestInfo(TestCase):
    def _data(self):
        self.data = {
            "info": {
                "contact": {
                    "name": "contact name",
                    "email": "contact email",
                    "url": "contact url",
                },
                "license": {"name": "", "url": ""},
                "title": "example",
                "version": "1.0.0",
                "termsOfService": "term of service",
                "description": "description",
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
        self.assertEqual(data.get("info"), self.data.get("info"))

    def tearDown(self) -> None:
        Deferred._deferred = []

        return super().tearDown()


class TestInfoDeferred(TestCase):
    def _data(self):
        self.data = {
            "info": {
                "contact": {
                    "name": "contact name",
                    "email": "contact email",
                    "url": "contact url",
                },
                "license": {"name": "", "url": ""},
                "title": "example",
                "version": "1.0.0",
                "termsOfService": "term of service",
                "description": "description",
            }
        }

    def set_deferred(self):
        self.deferred_data = {
            "title": "new title",
            "version": "new version",
            "termsOfService": "new termsOfService",
            "license_name": "new license_name",
            "license_url": "new license_url",
            "contact_name": "new contact_name",
            "contact_email": "new contact_email",
            "contact_url": "new contact_url",
            "description": "new description",
        }
        Deferred._deferred.append(
            (
                "api_info",
                (),
                self.deferred_data,
            )
        )

    def setUp(self) -> None:
        self._deferred_methods = []
        self._data()
        self.set_deferred()
        self.builder = OasBuilder(self.data)
        return super().setUp()

    def test_info_from_deferred(self):
        data = self.builder.get_data()
        self.assertEqual(
            data.get("info", {}).get("title", None),
            self.deferred_data.get("title", ""),
        )
        self.assertEqual(
            data.get("info", {}).get("version", None),
            self.deferred_data.get("version", ""),
        )
        self.assertEqual(
            data.get("info", {}).get("termsOfService", None),
            self.deferred_data.get("termsOfService", ""),
        )
        self.assertEqual(
            data.get("info", {}).get("description", None),
            self.deferred_data.get("description", ""),
        )
        self.assertEqual(
            data.get("info", {}).get("license", {}),
            {
                "name": self.deferred_data.get("license_name", ""),
                "url": self.deferred_data.get("license_url", ""),
            },
        )
        self.assertEqual(
            data.get("info", {}).get("contact", {}),
            {
                "name": self.deferred_data.get("contact_name", ""),
                "email": self.deferred_data.get("contact_email", ""),
                "url": self.deferred_data.get("contact_url", ""),
            },
        )

    def tearDown(self) -> None:
        Deferred._deferred = []

        return super().tearDown()


class TestDecorator(TestCase):
    def setUp(self) -> None:
        self.data = {
            "title": "new title",
            "version": "new version",
            "termsOfService": "new termsOfService",
            "license_name": "new license_name",
            "license_url": "new license_url",
            "contact_name": "new contact_name",
            "contact_email": "new contact_email",
            "contact_url": "new contact_url",
            "description": "new description",
        }
        api_info(**self.data)
        self.builder = OasBuilder(self.data)
        return super().setUp()

    def test_decorator(self):
        data = self.builder.get_data()
        self.assertEqual(
            data.get("info", {}).get("title", None),
            self.data.get("title", ""),
        )
        self.assertEqual(
            data.get("info", {}).get("version", None),
            self.data.get("version", ""),
        )
        self.assertEqual(
            data.get("info", {}).get("termsOfService", None),
            self.data.get("termsOfService", ""),
        )
        self.assertEqual(
            data.get("info", {}).get("description", None),
            self.data.get("description", ""),
        )
        self.assertEqual(
            data.get("info", {}).get("license", {}),
            {
                "name": self.data.get("license_name", ""),
                "url": self.data.get("license_url", ""),
            },
        )
        self.assertEqual(
            data.get("info", {}).get("contact", {}),
            {
                "name": self.data.get("contact_name", ""),
                "email": self.data.get("contact_email", ""),
                "url": self.data.get("contact_url", ""),
            },
        )

    def tearDown(self) -> None:
        Deferred._deferred = []

        return super().tearDown()
