from ..open_oas.builder.builder import OasBuilder
from unittest import TestCase
from ..open_oas.decorators import (
    Deferred,
    path_security_requirements,
    security_requirements,
)


class TestSetSecurityRequirements(TestCase):
    def test_and_or_false_empty_old(self):
        builder = OasBuilder()
        data = dict(
            security="BasicAuth",
            scopes=[],
            AND=False,
            OR=False,
            index=-1,
            old=[],
        )

        res = builder._set_security_requirements(**data)  # type: ignore
        self.assertEqual(res, [{"BasicAuth": []}])

    def test_and_or_false_value_old(self):
        builder = OasBuilder()
        data = dict(
            security="BasicAuth",
            scopes=[],
            AND=False,
            OR=False,
            index=-1,
            old=[{"OldAuth": []}],
        )

        res = builder._set_security_requirements(**data)  # type: ignore
        self.assertEqual(res, [{"BasicAuth": []}])

    def test_and_false_or_true_empty_old_default_index(self):
        builder = OasBuilder()
        data = dict(
            security="BasicAuth",
            scopes=[],
            AND=False,
            OR=True,
            index=-1,
            old=[],
        )

        res = builder._set_security_requirements(**data)  # type: ignore
        self.assertEqual(res, [{"BasicAuth": []}])

    def test_and_false_or_true_value_old_default_index(self):
        builder = OasBuilder()
        data = dict(
            security="BasicAuth",
            scopes=[],
            AND=False,
            OR=True,
            index=-1,
            old=[{"OldAuth": []}],
        )

        res = builder._set_security_requirements(**data)  # type: ignore
        self.assertEqual(res, [{"OldAuth": []}, {"BasicAuth": []}])

    def test_and_false_or_true_value_old_0_index(self):
        builder = OasBuilder()
        data = dict(
            security="BasicAuth",
            scopes=[],
            AND=False,
            OR=True,
            index=0,
            old=[{"OldAuth": []}],
        )

        res = builder._set_security_requirements(**data)  # type: ignore
        self.assertEqual(
            res,
            [
                {"BasicAuth": []},
                {"OldAuth": []},
            ],
        )

    def test_and_false_or_true_value_old_random_index(self):
        builder = OasBuilder()
        data = dict(
            security="BasicAuth",
            scopes=[],
            AND=False,
            OR=True,
            index=1,
            old=[{"VeryOldAuth": []}, {"OldAuth": []}],
        )

        res = builder._set_security_requirements(**data)  # type: ignore
        self.assertEqual(
            res,
            [
                {"VeryOldAuth": []},
                {"BasicAuth": []},
                {"OldAuth": []},
            ],
        )

    def test_and_true_or_false_empty_old_default_index(self):
        builder = OasBuilder()
        data = dict(
            security="BasicAuth",
            scopes=[],
            AND=True,
            OR=False,
            index=-1,
            old=[],
        )

        res = builder._set_security_requirements(**data)  # type: ignore
        self.assertEqual(res, [{"BasicAuth": []}])

    def test_and_true_or_false_value_old_default_index(self):
        builder = OasBuilder()
        data = dict(
            security="BasicAuth",
            scopes=[],
            AND=True,
            OR=False,
            index=-1,
            old=[{"OldAuth": []}],
        )

        res = builder._set_security_requirements(**data)  # type: ignore
        self.assertEqual(res, [{"BasicAuth": [], "OldAuth": []}])

    def test_and_true_or_false_value_old_non_default_index(self):
        builder = OasBuilder()
        data = dict(
            security="BasicAuth",
            scopes=[],
            AND=True,
            OR=False,
            index=0,
            old=[
                {"VeryOldAuth": []},
                {"OldAuth": []},
            ],
        )

        res = builder._set_security_requirements(**data)  # type: ignore
        self.assertEqual(
            res,
            [
                {"BasicAuth": [], "VeryOldAuth": []},
                {"OldAuth": []},
            ],
        )


class TestRootSecurityRequirements(TestCase):
    def test_decorator(self):
        security_requirements(
            "BasicAuth",
            [],
        )
        data = OasBuilder().get_data()
        self.assertEqual(
            data.get(
                "security",
            ),
            [{"BasicAuth": []}],
        )
        #
        security_requirements(
            "BearerAuth",
            [],
        )
        data = OasBuilder().get_data()
        self.assertEqual(
            data.get(
                "security",
            ),
            [{"BasicAuth": []}, {"BearerAuth": []}],
        )

    def tearDown(self) -> None:
        Deferred._deferred = []
        return super().tearDown()


class TestPathSecurityRequirements(TestCase):
    def run_tests(self, builder: OasBuilder):
        data = builder.get_data()
        self.assertEqual(
            data.get("paths", {})
            .get("/admin", {})
            .get("get", {})
            .get("security", {}),
            self.admin_auth,
        )
        self.assertEqual(
            data.get("paths", {})
            .get("/user", {})
            .get("get", {})
            .get("security", {}),
            self.user_auth,
        )

    # [] = or
    # {} = and

    def setUp(self) -> None:
        self.admin_auth = [
            {
                "Oath2": ["admin"],
            },
            {
                "AdminApiKey": [],
            },
        ]
        self.user_auth = [
            {
                "Oath2": ["user"],
                "BasicAuth": [],
            },
        ]

        return super().setUp()

    def test_data(self):

        data = {
            "paths": {
                "/admin": {
                    "get": {
                        "security": self.admin_auth,
                    },
                },
                "/user": {
                    "get": {
                        "security": self.user_auth,
                    },
                },
            }
        }

        builder = OasBuilder(data)

        self.run_tests(builder)

    def test_decorator(self):
        path_security_requirements(
            ["/admin"],
            ["get"],
            "Oath2",
            ["admin"],
        )
        path_security_requirements(
            ["/admin"],
            ["get"],
            "AdminApiKey",
            [],
        )
        #
        path_security_requirements(
            ["/user"],
            ["get"],
            "Oath2",
            ["user"],
        )
        path_security_requirements(
            ["/user"], ["get"], "BasicAuth", [], AND=True, OR=False
        )
        builder = OasBuilder()
        self.run_tests(builder)

    def tearDown(self) -> None:
        Deferred._deferred = []
        return super().tearDown()
