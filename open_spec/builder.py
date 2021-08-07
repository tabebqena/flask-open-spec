from ._utils import clean_parameters_list, merge_recursive
from ._parameters import VALID_METHODS_OPENAPI_V3
from typing import Any, Literal, Union, cast
from marshmallow import Schema, class_registry


class OasBuilder:
    data: dict = {}

    def __init__(
        self,
        data: dict = {},
        default_required=True,
        default_content_type="application/json",
        allowed_methods=VALID_METHODS_OPENAPI_V3,
    ) -> None:
        OasBuilder.data = data
        self.default_required = default_required
        self.default_content_type = default_content_type
        self.allowed_methods = allowed_methods

    def __validate__(self, path, method, schema):
        if path is not None and not path.startswith("/"):
            raise ValueError("path {0} should start with `/`".format(path))
        if (
            method is not None and not method in self.allowed_methods
        ):  # VALID_METHODS_OPENAPI_V3:
            raise ValueError(
                "method should be one of allowed methods {0}".format(
                    ", ".join(self.allowed_methods)
                )
            )
        schema_error = TypeError(
            "schema {0} should be subclass of `marshmallow.schema.Schema` \
                or dictionary\
                or name of the schema class   \
                ".format(
                schema
            )
        )
        if schema:
            valid = False
            if isinstance(schema, type) and issubclass(schema, Schema):
                valid = True
            elif type(schema) == str:
                sc = class_registry.get_class(cast(str, schema))
                if sc:
                    valid = True
            elif isinstance(schema, dict):
                valid = True
            if not valid:
                raise schema_error

    def request_body(
        self,
        path: str,
        method: Literal[
            "get", "post", "put", "patch", "delete", "head", "options", "trace"
        ],
        schema: Any,
        content_type: str = None,
        **kwargs
    ):
        mthd = method.lower()
        self.__validate__(path, mthd, schema)
        OasBuilder.data = cast(
            dict,
            merge_recursive(
                [
                    {
                        "paths": {
                            path: {
                                mthd: {
                                    "requestBody": {
                                        "content": {
                                            content_type
                                            or self.default_content_type: {
                                                "schema": schema
                                            }
                                        },
                                        "description": kwargs.get(
                                            "description", ""
                                        ),
                                        "required": kwargs.get(
                                            "required", self.default_required
                                        ),
                                    },
                                },
                            },
                        },
                    },
                    OasBuilder.data,
                ]
            ),
        )
        # self.data["paths"][path][mthd]["requestBody"] = request_body

    def response(
        self,
        path: str,
        method: Literal[
            "get", "post", "put", "patch", "delete", "head", "options", "trace"
        ],
        schema: Any,
        code: Union[int, str] = "default",
        content_type: str = None,
        description: str = "",
    ):
        mthd = method.lower()
        self.__validate__(path, mthd, schema)
        content_type = content_type or self.default_content_type

        OasBuilder.data = cast(
            dict,
            merge_recursive(
                [
                    {
                        "paths": {
                            path: {
                                mthd: {
                                    "responses": {
                                        str(code): {
                                            "content": {
                                                "schema": schema,
                                            },
                                            "description": description,
                                        },
                                    },
                                },
                            }
                        }
                    },
                    OasBuilder.data,
                ]
            ),
        )

        """self.data.setdefault("paths", {}).setdefault(path, {}).setdefault(
            mthd, {}
        ).setdefault("responses", {}).setdefault(str(code), {}).setdefault(
            "content", {}
        ).setdefault(
            content_type, {}
        ).setdefault(
            "schema", schema
        )
        self.data.setdefault("paths", {}).setdefault(path, {}).setdefault(
            mthd, {}
        ).setdefault("responses", {}).setdefault(str(code), {}).setdefault(
            "description", description
        )"""

    def security_reqs(
        self,
        path: str,
        method: Literal[
            "get", "post", "put", "patch", "delete", "head", "options", "trace"
        ],
        security: str,
        scopes=[],
        AND=False,
        OR=False,
    ):
        mthd = method.lower()
        self.__validate__(path, mthd, None)
        if AND and OR:
            raise ValueError("You should specify only one of AND/OR not both")

        old = (
            OasBuilder.data.setdefault("paths", {})
            .setdefault(path, {})
            .setdefault(mthd, {})
            .setdefault("security", [])
        )
        if old and AND:
            sec = old
            sec[-1].update({security: scopes})
            OasBuilder.data["paths"][path][mthd]["security"] = sec

        elif old and OR:
            sec = old + [{security: scopes}]
            OasBuilder.data["paths"][path][mthd]["security"] = sec
        else:
            OasBuilder.data["paths"][path][mthd]["security"] = [
                {security: scopes}
            ]

    def parameter(
        self,
        path: str,
        method: Literal[
            "get", "post", "put", "patch", "delete", "head", "options", "trace"
        ],
        in_,
        name,
        schema,
        description,
        **kwargs
    ):

        mthd = method.lower()
        self.__validate__(path, mthd, schema)
        required = kwargs.get("required", self.default_required)

        parameters = (
            OasBuilder.data.setdefault("paths", {})
            .setdefault(path, {})
            .setdefault(mthd, {})
            .setdefault("parameters", [])
        )
        param = {
            "in": in_,
            "name": name,
            "schema": schema,
            "description": description,
            "required": required,
        }
        parameters.append(param)
        OasBuilder.data["paths"][path][method][
            "parameters"
        ] = clean_parameters_list(parameters)

    def path_details(self, path: str, summary="", description="", servers=[]):
        path_data = OasBuilder.data.setdefault("paths", {}).setdefault(path, {})
        if summary:
            path_data["summary"] = summary
        if description:
            path_data["description"] = description
        if servers:
            path_data["servers"] = servers
        OasBuilder.data["paths"][path] = path_data
