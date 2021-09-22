from functools import lru_cache
from http import HTTPStatus
from logging import warning
from urllib.request import Request
from ..plugin.utils import import_by_path, resolve_schema_instance
from typing import TYPE_CHECKING, Dict, List, Optional, Union, cast
from flask import abort, g, jsonify, make_response

from flask import request

if TYPE_CHECKING:
    from ..open_oas import OpenOas

from .._parameters import rule_to_path
from ._utils import _resolve_oas_object, _get_row_oas, _get_request_body_data


class _RequestsAuthenticator:
    def __init__(self, open_oas: "OpenOas") -> None:
        self.open_oas = open_oas
        self.config = open_oas.config
        if self.config.authenticate_requests:
            open_oas.app.before_request(self.__authenticate_request)
        else:
            return

        self.__set_on_unauthenticated_handler(
            self.config.on_unauthenticated_handler
            or self._default_on_unauthenticated_handler
        )
        self.row_oas = {}

    def __set_on_unauthenticated_handler(self, handler):
        self.on_unauthenticated_handler = handler

    def _default_on_unauthenticated_handler(self):
        data = {"code": str(HTTPStatus.UNAUTHORIZED)}
        if self.config.default_unauthorized_message:
            data["message"] = self.config.default_unauthorized_message
        return make_response(jsonify(data), HTTPStatus.UNAUTHORIZED)

    def _get_root_security_scheme(self):
        return _get_row_oas(self).get("security", [])

    @lru_cache(maxsize=50)
    def __get_path_security_requirements(self, path: str, method: str):
        oas = _get_row_oas(self)
        scheme = (
            oas.get("paths", {})
            .get(path, {})
            .get(method.lower(), {})
            .get("security", [])
        )
        if not scheme:
            scheme = self._get_root_security_scheme()
        scheme.sort(key=lambda s: 1 if len(s.keys()) > 1 else -1)
        return scheme

    def __authenticate_request(self):
        path = rule_to_path(request.url_rule)
        method = request.method
        reqs: list = self.__get_path_security_requirements(path, method)
        is_authenticated: bool = self.__is_authenticated(reqs)
        if not is_authenticated:
            return self.on_unauthenticated_handler()

    def __is_authenticated(self, reqs: list):
        res = []
        # req = may be dict or list of
        # obj = {"schemaName": [schemaScopes]}
        # object dict may has many keys also
        # {"schemaName2": [schemaScopes], "schemaName2": [schemaScopes]}
        for req in reqs:
            res.append(self.__is_security_requirements_met(req))
        return True in res

    def __is_security_requirements_met(
        self, requirement: Union[List[dict], Dict[str, dict]]
    ):
        if isinstance(requirement, dict):
            if len(requirement.keys()) > 1:
                res = []
                for k, v in requirement.items():
                    res.append(self.__is_security_requirements_met([{k: v}]))
                return False not in res
            else:
                k = list(cast(dict, requirement).keys())[0]
                rv = self.__apply_scheme_handler(k)

                return rv

        elif isinstance(requirement, list):
            res = []
            for s in requirement:
                res.append(self.__is_security_requirements_met(s))
            return True in res

    def __apply_scheme_handler(self, scheme_name: str):
        scheme = (
            _get_row_oas(self)
            .get("components", {})
            .get("securitySchemes", {})
            .get(scheme_name, {})
        )
        handler = self.__get_handler(scheme_name)
        if callable(handler):
            info = self.__parse_scheme_info(scheme)
            try:
                if not handler(scheme, info):
                    return False
                return True
            except Exception as e:
                warning(e)
                return False
        return False

    @lru_cache(maxsize=50)
    def __get_handler(self, scheme_name: str):
        xhandler = (
            _get_row_oas(self)
            .get("components", {})
            .get("securitySchemes", {})
            .get(scheme_name, {})
            .get("x-handler", None)
        )
        if not xhandler:
            xhandler = self.config.is_authenticated_handler
        if isinstance(xhandler, str):
            return import_by_path(xhandler)
        return xhandler

    def __parse_scheme_info(self, scheme: dict):
        type_ = scheme.get("type", "").strip()
        sch = scheme.get("scheme", "").strip()
        if type_ == "http":
            if sch == "basic":
                return (
                    request.headers.get("Authorization", "")
                    .split("Basic")[-1]
                    .strip()
                )
            if sch == "bearer":
                return (
                    request.headers.get("Authorization", "")
                    .split("Bearer")[-1]
                    .strip()
                )
        elif type_ == "apiKey":
            in_ = scheme.get("in", "").strip()
            name = scheme.get("name", "").strip()

            if in_ == "header":
                return request.headers.get(name)
            elif in_ == "query":
                return request.args.get(name)

            elif in_ == "cookie":
                return request.cookies.get(name)
