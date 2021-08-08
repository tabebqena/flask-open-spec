import re
from flask import current_app

from typing import Dict, List, Literal

import werkzeug.routing
from flask import current_app
from werkzeug.routing import Rule


#
#

VALID_METHODS_OPENAPI_V3 = [
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "head",
    "options",
    "trace",
]
#
PATH_RE = re.compile(r"<(?:[^:<>]+:)?([^<>]+)>")


def rule_to_path(rule):
    return PATH_RE.sub(r"{\1}", rule.rule)


def app_path_oas_path(app_path):
    return PATH_RE.sub(r"{\1}", app_path)


#
def get_app_paths() -> Dict[str, List[str]]:
    rules: List[Rule] = current_app.url_map._rules
    paths: Dict[str, List[str]] = {}
    for r in rules:
        path = rule_to_path(r)
        methods: List[str] = __get_valid_methods(r)
        paths[path] = methods
    return paths


DEFAULT_TYPE = ("string", None)
CONVERTER_MAPPING = {
    werkzeug.routing.UnicodeConverter: ("string", None),
    werkzeug.routing.IntegerConverter: ("integer", "int32"),
    werkzeug.routing.FloatConverter: ("number", "float"),
}
#
def __rule_to_params(rule, overrides=None, long_stub=False):
    overrides = overrides or {}
    result = [
        __argument_to_param(
            argument, rule, overrides.get(argument, {}), long_stub
        )
        for argument in rule.arguments
    ]
    for key in overrides.keys():
        if overrides[key].get("in") in ("header", "query"):
            overrides[key]["name"] = overrides[key].get("name", key)
            result.append(overrides[key])
    return result


def __argument_to_param(argument, rule, override=None, long_stub=False):
    param = {
        "in": "path",
        "name": argument,
        "required": True,
        "schema": {},
    }
    if long_stub:
        param.update(
            {
                "description": "",
                "deprecated": False,
                "allowEmptyValue": False,
            }
        )
    type_, format_ = CONVERTER_MAPPING.get(
        type(rule._converters[argument]), DEFAULT_TYPE
    )
    param["schema"]["type"] = type_
    if format_ is not None:
        param["schema"]["format"] = format_
    if rule.defaults and argument in rule.defaults:
        param["schema"]["default"] = rule.defaults[argument]
    param.update(override or {})
    return param


def __get_parameter(parameters, name):
    if not parameters:
        return None
    for p in parameters:
        if p.get("name", None) == name:
            return p


def __merge_parameters(default_parameters: List, user_parameters: List):
    res = []

    if not default_parameters:
        res = user_parameters
    for def_param in default_parameters:
        user_param = __get_parameter(user_parameters, def_param.get("name", ""))
        if user_param:
            def_param.update(user_param)
        res.append(def_param)
    return res


def preserve_user_edits(
    default_params: dict,
    user_params: dict,
    allowed_methods=VALID_METHODS_OPENAPI_V3,
):
    res = {}
    if not default_params:
        default_params = {}
    if not user_params:
        user_params = {}
    paths = list(
        set(
            list(default_params.get("paths", {}).keys())
            + list(user_params.get("paths", {}).keys())
        )
    )
    for path in paths:
        res.setdefault("paths", {}).setdefault(path, {}).setdefault(
            "parameters", []
        )
        res["paths"][path]["parameters"] = __merge_parameters(
            default_params.get("paths", {}).get(path, {}).get("parameters", []),
            user_params.get("paths", {}).get(path, {}).get("parameters", []),
        )
        methods = set(
            list(default_params.get("paths", {}).get(path, {}).keys())
            + list(user_params.get("paths", {}).get(path, {}).keys())
        )

        for method in methods:
            """if method not in VALID_METHODS_OPENAPI_V3:
            continue"""
            if method not in allowed_methods:
                continue
            res.setdefault("paths", {}).setdefault(path, {}).setdefault(
                method, {}
            ).setdefault("parameters", [])
            res["paths"][path][method]["parameters"] = __merge_parameters(
                default_params.get("paths", {})
                .get(path, {})
                .get(method, {})
                .get("parameters", []),
                user_params.get("paths", {})
                .get(path, {})
                .get(method, {})
                .get("parameters", []),
            )

    return res


def __get_valid_methods(rule: Rule, version=3):
    excluded_methods = {"head"}
    _mthds: set = rule.methods
    methods: List[str] = []
    valid_methods = VALID_METHODS_OPENAPI_V3  # [version]
    for method in _mthds:
        if method.lower() in (set(valid_methods) - excluded_methods):
            methods.append(method.lower())
    return methods


def extract_path_parameters(
    # document_options=False,
    long_stub=False,
    allowed_methods=VALID_METHODS_OPENAPI_V3,
):
    data = {}
    rules: List[Rule] = current_app.url_map._rules

    for r in rules:
        path = rule_to_path(r)
        params = __rule_to_params(r, long_stub=long_stub) or []
        methods = __get_valid_methods(r)
        for method in methods:
            """if method.lower() == "options" and not document_options:
            continue"""
            if method.lower() not in allowed_methods:
                continue
            data.setdefault("paths", {}).setdefault(path, {}).setdefault(
                method, {}
            ).setdefault("parameters", params)
    return data
