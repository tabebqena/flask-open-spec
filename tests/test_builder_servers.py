from ..open_spec.builder.builder import OasBuilder
from unittest import TestCase
from ..open_spec.decorators import Deferred, api_server


class TestSevers(TestCase):
    def _data(self):
        self.data = {
            "servers": [
                {
                    "url": "server 1 url",
                    "description": "server 1 description",
                },
                {
                    "url": "server 2 url",
                    "description": "server 2 description",
                },
            ]
        }

    def setUp(self) -> None:
        self._data()
        self.builder = OasBuilder(
            self.data,
        )
        return super().setUp()

    def test_info_from_data(self):
        data = self.builder.get_data()
        self.assertEqual(data.get("servers"), self.data.get("servers"))

    def tearDown(self) -> None:
        return super().tearDown()


class TestDeferred(TestCase):
    def _data(self):
        return {
            "servers": [
                {
                    "url": "server 1 url",
                    "description": "server 1 description",
                },
                {
                    "url": "server 2 url",
                    "description": "server 2 description",
                },
            ]
        }

    def set_deferred(self):
        self.servers = [
            {
                "url": "server 1 url",
                "description": "new server 1 description",
            },
            {
                "url": "server 2 url",
                "description": "new server 2 description",
            },
            {
                "url": "server 3 url",
                "description": "new server 3 description",
            },
        ]
        self._deferred_methods = []
        for s in self.servers:
            Deferred._deferred.append(
                (
                    "api_server",
                    (s.get("url"), s.get("description")),
                    {},
                )
            )

    def setUp(self) -> None:
        self._data()
        self.set_deferred()
        self.builder = OasBuilder(self._data())
        return super().setUp()

    def test_from_deferred(self):
        data = self.builder.get_data().get("servers", [])
        for server in data:
            input_server = {}
            for s in self.servers:
                if s["url"] == server["url"]:
                    input_server = s
            self.assertEqual(server, input_server)

    def tearDown(self) -> None:
        Deferred._deferred = []
        
        return super().tearDown()


class TestDecorator(TestCase):
    def setUp(self) -> None:
        self.servers = [
            {
                "url": "server 1 url",
                "description": "new server 1 description",
            },
            {
                "url": "server 2 url",
                "description": "new server 2 description",
            },
            {
                "url": "server 3 url",
                "description": "new server 3 description",
            },
        ]
        for s in self.servers:
            api_server(**s)
        self.builder = OasBuilder()
        return super().setUp()

    def test_decorator(self):
        data = self.builder.get_data()
        self.assertEqual(data.get("servers", []), self.servers)
    def tearDown(self) -> None:
        Deferred._deferred = []
        
        return super().tearDown()