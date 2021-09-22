from functools import wraps

# from .builder import oas_builder
from typing import Any, List, Literal, Optional, Union
from ._parameters import VALID_METHODS_OPENAPI_V3, app_path_oas_path


class Deferred:
    _deferred = []


def api_info(
    title,
    version="1.0.0",
    termsOfService=None,
    license_name=None,
    license_url=None,
    contact_name=None,
    contact_email=None,
    contact_url=None,
    description=None,
):
    Deferred._deferred.append(
        (
            "api_info",
            (),
            {
                "title": title,
                "version": version,
                "termsOfService": termsOfService,
                "license_name": license_name,
                "license_url": license_url,
                "contact_name": contact_name,
                "contact_email": contact_email,
                "contact_url": contact_url,
                "description": description,
            },
        )
    )


def api_external_docs(url, description=""):
    Deferred._deferred.append(
        (
            "api_external_docs",
            (
                url,
                description,
            ),
            {},
        )
    )


def api_tag(name, description="", external_docs_url=""):
    Deferred._deferred.append(
        (
            "api_tag",
            (name, description, external_docs_url),
            {},
        )
    )


def api_server(url, description):
    Deferred._deferred.append(
        (
            "api_server",
            (url, description),
            {},
        )
    )


def api_basic_security_scheme(name):
    Deferred._deferred.append(
        (
            "api_security_scheme",
            (
                name,
                {"type": "http", "scheme": "basic"},
            ),
            {},
        )
    )


def api_bearer_security_scheme(name, bearer_format="JWT"):

    Deferred._deferred.append(
        (
            "api_security_scheme",
            (
                name,
                {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": bearer_format,
                },
            ),
            {},
        )
    )


def api_key_security_schema(
    name: str,
    in_: Literal["header", "query", "cookie"] = "header",
    location_name: str = "X-API-KEY",
):
    Deferred._deferred.append(
        (
            "api_security_scheme",
            (
                name,
                {
                    "type": "apiKey",
                    "in": in_,
                    "name": location_name,
                },
            ),
            {},
        )
    )


def component_schema(schema, schema_kwargs={}):
    Deferred._deferred.append(
        (
            "component_schema",
            (schema, schema_kwargs),
            {},
        )
    )


def component_request_body(
    request_body_name: str, content_type: str, schema: Any, **kwargs
):
    Deferred._deferred.append(
        (
            "component_request_body",
            (request_body_name, content_type, schema),
            {**kwargs},
        )
    )


def component_parameter(
    parameter_name, in_, name, schema, description="", **kwargs
):
    Deferred._deferred.append(
        (
            "component_parameter",
            (
                parameter_name,
                in_,
                name,
                schema,
            ),
            {"description": description, **kwargs},
        )
    )


def component_response(
    response_name: Optional[str],
    content_type: str,
    schema: Any,
    description: str = "",
    schema_kwargs={},
):
    Deferred._deferred.append(
        (
            "component_response",
            (),
            {
                "response_name": response_name,
                "content_type": content_type,
                "schema": schema,
                "description": description,
                "schema_kwargs": schema_kwargs,
            },
        )
    )


def component_header(header_name, schema, description=""):
    Deferred._deferred.append(
        (
            "component_header",
            (
                header_name,
                schema,
            ),
            {"description": description},
        )
    )


#
#
#
def path_request_body(
    schema,
    paths: List[str],
    methods: List[str] = ["*"],
    content_types: List[str] = ["application/json"],
    required=True,
    description="",
    **kwargs,
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
    for path in paths:

        path_ = app_path_oas_path(path)
        for method in methods:
            method = method.lower()
            for content_type in content_types:
                Deferred._deferred.append(
                    (
                        "path_request_body",
                        (),
                        {
                            "path": path_,
                            "method": method,
                            "schema": schema,
                            "content_type": content_type,
                            "description": description,
                            "required": required,
                            **kwargs,
                        },
                    )
                )

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def path_response(
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
    for path in paths:
        path_ = app_path_oas_path(path)
        for method in methods:
            method = method.lower()
            for code in codes:
                for content_type in content_types:
                    Deferred._deferred.append(
                        (
                            "path_response",
                            (),
                            {
                                "path": path_,
                                "method": method,
                                "code": code,
                                "schema": schema,
                                "content_type": content_type,
                                "description": description,
                            },
                        )
                    )

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


#
#


def path_details(paths: List[str], summary, description="", servers=[]):
    if not isinstance(paths, list):
        raise TypeError(
            "`paths` should be list of paths, not {0}".format(type(paths))
        )
    for path in paths:
        path_ = app_path_oas_path(path)
        Deferred._deferred.append(
            (
                "path_details",
                (),
                dict(
                    path=path_,
                    summary=summary,
                    description=description,
                    servers=servers,
                ),
            ),
        )

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def path_parameter(
    paths: List[str],
    in_=None,
    name=None,
    schema=None,
    description=None,
    **kwargs,
):
    if not isinstance(paths, list):
        raise TypeError(
            "`paths` should be list of paths, not {0}".format(type(paths))
        )
    if in_ is None or name is None or schema is None:
        raise TypeError("`in_`, `name`, and `schema` can't be None")

    for path in paths:
        path_ = app_path_oas_path(path)
        Deferred._deferred.append(
            (
                "path_parameter",
                (),
                dict(
                    path=path_,
                    in_=in_,
                    name=name,
                    schema=schema,
                    description=description,
                    **kwargs,
                ),
            )
        )

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


# root level or operation level only


def security_requirements(
    security: str = None,
    scopes=[],
    AND=False,
    OR=True,
    index=-1,
):
    Deferred._deferred.append(
        (
            "root_security_requirements",
            (),
            dict(
                security=security,
                scopes=scopes,
                AND=AND,
                OR=OR,
                index=index,
            ),
        )
    )

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def path_security_requirements(
    paths: List[str] = [],
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
    OR=True,
    index=-1,
):
    if not isinstance(paths, list):
        raise TypeError(
            "`paths` should be list of paths, not {0}".format(type(paths))
        )
    if len(paths) == 0:
        raise ValueError("`paths` could not be empty list")
    if AND and OR:
        raise ValueError("You should specify only one of AND/OR not both")

    if security is None:
        raise TypeError("`security` parameter can't be None")
    for method in methods:
        method = method.lower()
        if method not in VALID_METHODS_OPENAPI_V3:
            raise ValueError(
                "methods should be list of valid HTTP methods or ['*']"
            )
    if not methods:
        methods = ["*"]  # type: ignore
    for path in paths:
        path_ = app_path_oas_path(path)
        for method in methods:
            method = method.lower()

            Deferred._deferred.append(
                (
                    "path_security_requirements",
                    (),
                    dict(
                        path=path_,
                        method=method,
                        security=security,
                        scopes=scopes,
                        AND=AND,
                        OR=OR,
                        index=index,
                    ),
                )
            )

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator
