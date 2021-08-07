from functools import wraps
from .builder import OasBuilder
from typing import List, Literal, Union
from ._parameters import VALID_METHODS_OPENAPI_V3, app_path_oas_path


def request_body(
    schema,
    paths: List[str],
    methods: List[str] = ["*"],
    content_types: List[str] = ["application/json"],
    required=True,
    description="",
    **kwargs
):
    if not isinstance(paths, list):
        raise TypeError(
            "`paths` should be list of paths, not {0}".format(type(paths))
        )
    for method in methods:
        method = method.lower()
        if method != "*" and method not in VALID_METHODS_OPENAPI_V3:
            raise ValueError(
                "methods should be list of valid HTTP methods or ['*']"
            )
    if not isinstance(content_types, list):
        raise TypeError(
            "`content_types` should be list of TYPES as [`application/json`], not {0}".format(
                type(content_types)
            )
        )

    def decorator(func):

        for path in paths:
            path_ = app_path_oas_path(path)
            for method in methods:
                method = method.lower()
                for content_type in content_types:
                    OasBuilder().request_body(
                        path_,
                        method,
                        schema,
                        content_type,
                        **{
                            "description": description,
                            "required": required,
                            **kwargs,
                        }
                    )
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def response(
    schema,
    paths: List[str],
    methods: List[
        Literal[
            "get",
            "post",
            "put",
            "patch",
            "delete",
            "head",
            "options",
            "trace",
            "*",
        ]
    ] = ["*"],
    codes: List[Union[int, str]] = ["default"],
    content_types: List[str] = ["application/json"],
    description: str = "",
):
    if not isinstance(paths, list):
        raise TypeError(
            "`paths` should be list of paths, not {0}".format(type(paths))
        )
    for method in methods:
        method = method.lower()
        if method != "*" and method not in VALID_METHODS_OPENAPI_V3:
            raise ValueError(
                "methods should be list of valid HTTP methods or ['*']"
            )
    if not isinstance(content_types, list):
        raise TypeError(
            "`content_types` should be list of TYPES as [`application/json`], not {0}".format(
                type(content_types)
            )
        )
    if not isinstance(codes, list):
        raise TypeError(
            "`codes` should be list of TYPES as [`200`, `404`, 'default'], not {0}".format(
                type(codes)
            )
        )

    def decorator(func):
        for path in paths:
            path_ = app_path_oas_path(path)
            for method in methods:
                method = method.lower()
                for code in codes:
                    for content_type in content_types:
                        OasBuilder().response(
                            path=path_,
                            method=method,
                            code=code,
                            schema=schema,
                            content_type=content_type,
                            description=description,
                        )

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def path_details(paths: List[str], summary, description="", servers=[]):
    if not isinstance(paths, list):
        raise TypeError(
            "`paths` should be list of paths, not {0}".format(type(paths))
        )

    def decorator(func):
        for path in paths:
            path_ = app_path_oas_path(path)
            OasBuilder().path_details(
                path=path_,
                summary=summary,
                description=description,
                servers=servers,
            )

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def parameter(
    paths: List[str],
    methods: List[
        Literal[
            "get",
            "post",
            "put",
            "patch",
            "delete",
            "head",
            "options",
            "trace",
            "*",
        ]
    ] = ["*"],
    in_=None,
    name=None,
    schema=None,
    description=None,
    **kwargs
):
    if not isinstance(paths, list):
        raise TypeError(
            "`paths` should be list of paths, not {0}".format(type(paths))
        )
    if in_ is None or name is None or schema is None:
        raise TypeError("`in_`, `name`, and `schema` can't be None")
    for method in methods:
        method = method.lower()
        if method != "*" and method not in VALID_METHODS_OPENAPI_V3:
            raise ValueError(
                "methods should be list of valid HTTP methods or ['*']"
            )

    def decorator(func):
        for path in paths:
            path_ = app_path_oas_path(path)
            for method in methods:
                method = method.lower()
                OasBuilder().parameter(
                    path_, method, in_, name, schema, description, **kwargs
                )

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def security_reqs(
    paths: List[str],
    methods: List[
        Literal[
            "get",
            "post",
            "put",
            "patch",
            "delete",
            "head",
            "options",
            "trace",
            "*",
        ]
    ] = ["*"],
    security: str = None,
    scopes=[],
    AND=False,
    OR=False,
):
    if not isinstance(paths, list):
        raise TypeError(
            "`paths` should be list of paths, not {0}".format(type(paths))
        )
    if security is None:
        raise TypeError("`security` parameter can't be None")
    for method in methods:
        method = method.lower()
        if method != "*" and method not in VALID_METHODS_OPENAPI_V3:
            raise ValueError(
                "methods should be list of valid HTTP methods or ['*']"
            )

    def decorator(func):
        for path in paths:
            path_ = app_path_oas_path(path)
            for method in methods:
                method = method.lower()
                OasBuilder().security_reqs(
                    path_, method, security, scopes, AND, OR
                )

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator
