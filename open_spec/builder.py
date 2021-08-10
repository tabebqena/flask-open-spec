from ._utils import clean_parameters_list, merge_recursive
from ._parameters import VALID_METHODS_OPENAPI_V3
from typing import Any, Literal, Optional, Union, cast
from marshmallow import Schema, class_registry
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin


class OasBuilder:
    """
    Builder class to create the open api specifications at runtime.
    The generated spec will be loaded by the `OpenSpec` object.
    """

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
        # self.allowed_methods = allowed_methods + ["*"]

    @staticmethod
    def __validate__(path, method, schema):
        allowed_methods = VALID_METHODS_OPENAPI_V3 + ["*"]
        if path is not None and not path.startswith("/"):
            raise ValueError("path {0} should start with `/`".format(path))
        if (
            method is not None and not method in allowed_methods
        ):  # VALID_METHODS_OPENAPI_V3:
            raise ValueError(
                "method should be one of allowed methods {0}".format(
                    ", ".join(allowed_methods)
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
            elif isinstance(schema, Schema):
                valid = True
            elif type(schema) == str:
                sc = class_registry.get_class(cast(str, schema))
                if sc:
                    valid = True
            elif isinstance(schema, dict):
                valid = True
            if not valid:
                raise schema_error

    @staticmethod
    def info(
        title,
        version="1.0.0",
        termsOfService=None,
        license_name=None,
        license_url=None,
        contact_name=None,
        contact_email=None,
        contact_url=None,
        description=None,
    ) -> None:
        """
        Add/edit the info section of the api.

        [extended_summary]

        Args:
          title: The api title
          version:  (Default value = "1.0.0")
          termsOfService: text describing the term of service of this api (Default value = None)
          license_name:  (Default value = None)
          license_url:  (Default value = None)
          contact_name:  (Default value = None)
          contact_email:  (Default value = None)
          contact_url:  (Default value = None)
          description:  description of the api (Default value = None)

        Returns:
        """
        OasBuilder.data = cast(
            dict,
            merge_recursive(
                [
                    {
                        "info": {
                            "title": title,
                            "version": version,
                            "termsOfService": termsOfService,
                            "license": {
                                "name": license_name,
                                "url": license_url,
                            },
                            "contact": {
                                "name": contact_name,
                                "email": contact_email,
                                "url": contact_url,
                            },
                            "description": description,
                        },
                    },
                    OasBuilder.data,
                ]
            ),
        )

    @staticmethod
    def externalDocs(url, description=""):
        """
        Add/edit externalDocs section of the api

        Args:
          url: url to the external docs
          description:  (Default value = "")

        Returns:

        """
        OasBuilder.data = cast(
            dict,
            merge_recursive(
                [
                    {
                        "externalDocs": {
                            "url": url,
                            "description": description,
                        }
                    },
                    OasBuilder.data,
                ]
            ),
        )

    @staticmethod
    def tag(name, description="", external_docs_url=""):
        """
        Add tag to the tags section of the api.

        Args:
          name: tag name
          description:  (Default value = "")
          external_docs_url:  (Default value = "")

        Returns:

        Examples:

        >>> OasBuilder.tag("MyTag")
        >>> print( OasBuilder.data["tags"] )
        [{"name": "MyTag", "description": ""}]
        """
        tag = {
            "name": name,
            "description": description,
        }
        if external_docs_url:
            tag["externalDocs"] = {
                "url": external_docs_url,
            }
        OasBuilder.data = cast(
            dict,
            merge_recursive(
                [
                    {"tags": [tag]},
                    OasBuilder.data,
                ]
            ),
        )

    @staticmethod
    def server(url, description):
        """
        Add server to the servers section of the api

        Args:
          url: server url
          description: server description

        Returns:

        Examples:

        >>> OasBuilder.server("http://spec.host.com", "spec server")
        >>> print( OasBuilder.data["servers"] )
        [{"url": "http://spec.host.com", "description": "spec server"}]

        """
        OasBuilder.data = cast(
            dict,
            merge_recursive(
                [
                    {"servers": [{"url": url, "description": description}]},
                    OasBuilder.data,
                ]
            ),
        )

    @staticmethod
    def basic_security_schema(name: str):
        """
        api_key_security_schema generate apiKey authentivation schema and storing it in the api components

        Args:
          name: str:  arbitrary name for the security scheme

        Returns: None

        Examples:

        >>> OasBuilder.basic_security_schema("basicAuth")
        >>> print(OasBuilder.data["components"]["securitySchemes"])
        >>> {""basicAuth"": {"type": "http", "scheme": "basic"}}

        Note: The securitySchemes section alone is not enough; you must also use security for the API key to have effect.
        security can also be set on the operation level instead of globally.

        security:
        - basicAuth: []

        """
        OasBuilder.data = cast(
            dict,
            merge_recursive(
                [
                    {
                        "components": {
                            "securitySchemes": {
                                name: {"type": "http", "scheme": "basic"}
                            }
                        }
                    },
                    OasBuilder.data,
                ]
            ),
        )

    @staticmethod
    def api_key_security_schema(
        name: str,
        in_: Literal["header", "query", "cookie"] = "header",
        location_name: str = "X-API-KEY",
    ):
        """api_key_security_schema generate apiKey authentivation schema and storing it in the api components

        Args:
          name(str): arbitrary name for the security scheme
          in_(Literal[, optional): where the security key will be sent, can be "header", "query" or "cookie" , defaults to "header"
          location_name(str, optional): name of the header, query parameter or cookie], defaults to "X-API-KEY"
          name: str:
          in_: Literal["header":
          "query":
          "cookie"]:  (Default value = "header")
          location_name: str:  (Default value = "X-API-KEY")

        Returns: None


        Examples:

        This example defines an API key named X-API-Key sent as a request header X-API-Key: <key>.
           The key name ApiKeyAuth is an arbitrary name for
           the security scheme (not to be confused with the API key name,
           which is specified by the name key). The name ApiKeyAuth is used again
           in the security section to apply this security scheme to the API.

        >>> OasBuilder.api_key_security_schema("ApiKeyAuth", in_="header", location_name="X-API-Key")
        >>> print(OasBuilder.data["components"]["securitySchemes"])
        >>> {"ApiKeyAuth": {"type": "apiKey",  "in": "header" ,"name": "X-API-Key"}}

        Note: The securitySchemes section alone is not enough; you must also use security for the API key to have effect.
        security can also be set on the operation level instead of globally.

        security:
        - ApiKeyAuth: []

        """
        OasBuilder.data = cast(
            dict,
            merge_recursive(
                [
                    {
                        "components": {
                            "securitySchemes": {
                                name: {
                                    "type": "apiKey",
                                    "in": in_,
                                    "name": location_name,
                                }
                            }
                        }
                    },
                    OasBuilder.data,
                ]
            ),
        )

    @staticmethod
    def bearer_security_schema(name: str, bearerFormat: str = "JWT"):
        """
        bearer_security_schema generate bearer authentivation schema and storing it in the api components

        Args:
            name (str): [description]
            bearerFormat (str, optional): [description]. Defaults to "JWT".


        Returns: None

        Examples:

        >>> OasBuilder.bearer_security_schema("bearerAuth")
        >>> print(OasBuilder.data["components"]["securitySchemes"])
        >>> {"bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}}

        Note: The securitySchemes section alone is not enough; you must also use security for the API key to have effect.
        security can also be set on the operation level instead of globally.

        security:
        - bearerAuth: []

        """
        OasBuilder.data = cast(
            dict,
            merge_recursive(
                [
                    {
                        "components": {
                            "securitySchemes": {
                                name: {
                                    "type": "http",
                                    "scheme": "bearer",
                                    "bearerFormat": bearerFormat,
                                }
                            }
                        }
                    },
                    OasBuilder.data,
                ]
            ),
        )

    @staticmethod
    def component_schema(schema):
        OasBuilder.__validate__(None, None, schema)

        spec = APISpec("title", "1", "3.0.2", plugins=[MarshmallowPlugin()])
        spec.path(
            "/invalid",
            operations={
                "get": {
                    "responses": {
                        "default": {
                            "content": {"application/json": {"schema": schema}}
                        }
                    }
                },
            },
        )
        dict_ = spec.to_dict()
        name = list(dict_["components"]["schemas"].keys())[0]
        schema_data = dict_["components"]["schemas"][name]
        OasBuilder.data = cast(
            dict,
            merge_recursive(
                [
                    {"components": {"schemas": {name: schema_data}}},
                    OasBuilder.data,
                ]
            ),
        )
        return name

    @staticmethod
    def component_response(
        schema: Any,
        response_name: Optional[str],
        content_type: str,
        description: str = "",
    ):
        OasBuilder.__validate__(None, None, schema)

        spec = APISpec("title", "1", "3.0.2", plugins=[MarshmallowPlugin()])
        spec.path(
            "/invalid",
            operations={
                "get": {
                    "responses": {
                        "default": {
                            "content": {
                                content_type: {
                                    "schema": schema,
                                }
                            },
                            "description": description,
                        },
                    }
                },
            },
        )
        dict_ = spec.to_dict()
        response_data = (
            dict_.get("paths", {})
            .get("/invalid", {})
            .get("get", {})
            .get("responses", {})
            .get("default", {})
        )
        schemas = dict_.get("components", {}).get("schemas", {})
        schema_name = list(schemas.keys())[0]
        schema_data = (
            dict_.get("components", {}).get("schemas", {}).get(schema_name)
        )

        OasBuilder.data = cast(
            dict,
            merge_recursive(
                [
                    {
                        "components": {
                            "responses": {response_name: response_data},
                            "schemas": {schema_name: schema_data},
                        },
                    },
                    OasBuilder.data,
                ],
            ),
        )

    @staticmethod
    def component_request_body(
        schema: Any, content_type: str, request_body_name: str, **kwargs
    ):
        OasBuilder.__validate__(None, None, schema)
        spec = APISpec("title", "1", "3.0.2", plugins=[MarshmallowPlugin()])
        spec.path(
            "/invalid",
            operations={
                "get": {
                    "requestBody": {
                        "content": {
                            content_type: {
                                "schema": schema,
                            }
                        },
                    }
                },
            },
        )
        dict_ = spec.to_dict()
        body_data = (
            dict_.get("paths", {})
            .get("/invalid", {})
            .get("get", {})
            .get("requestBody", {})
        )
        schemas = dict_.get("components", {}).get("schemas", {})
        schema_name = list(schemas.keys())[0]
        schema_data = (
            dict_.get("components", {}).get("schemas", {}).get(schema_name)
        )

        OasBuilder.data = cast(
            dict,
            merge_recursive(
                [
                    {
                        "components": {
                            "requestBodies": {request_body_name: body_data},
                            "schemas": {schema_name: schema_data},
                        },
                    },
                    OasBuilder.data,
                ]
            ),
        )
        # self.data["paths"][path][mthd]["requestBody"] = request_body

    @staticmethod
    def component_parameter(
        parameter_name, in_, name, schema, description="", **kwargs
    ):
        OasBuilder.__validate__(None, None, schema)

        required = kwargs.get("required", False)

        param = {
            "in": in_,
            "name": name,
            "schema": schema,
            "description": description,
            "required": required,
        }

        spec = APISpec("title", "1", "3.0.2", plugins=[MarshmallowPlugin()])
        spec.path("/invalid", operations={"get": {"parameters": [param]}})
        dict_ = spec.to_dict()
        param_data = (
            dict_.get("paths", {})
            .get("/invalid", {})
            .get("get", {})
            .get("parameters", [])[0]
        )

        OasBuilder.data = cast(
            dict,
            merge_recursive(
                [
                    {
                        "components": {
                            "parameters": {parameter_name: param_data},
                            #     "schemas": {schema_name: schema_data},
                        },
                    },
                    OasBuilder.data,
                ]
            ),
        )

    @staticmethod
    def component_header(header_name, schema, description=""):
        OasBuilder.__validate__(None, None, schema)
        spec = APISpec("title", "1", "3.0.2", plugins=[MarshmallowPlugin()])
        spec.path(
            "/invalid",
            operations={
                "get": {
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "string",
                                    },
                                }
                            },
                            "headers": {
                                header_name: {
                                    "schema": schema,
                                    "description": description,
                                }
                            },
                        },
                    }
                }
            },
        )
        dict_ = spec.to_dict()
        header_data = (
            dict_.get("paths", {})
            .get("/invalid", {})
            .get("get", {})
            .get("responses", {})
            .get("200", {})
            .get("headers", {})
            .get(header_name, {})
        )

        schemas = dict_.get("components", {}).get("schemas", {})
        schema_name = list(schemas.keys())[0]
        schema_data = (
            dict_.get("components", {}).get("schemas", {}).get(schema_name)
        )

        OasBuilder.data = cast(
            dict,
            merge_recursive(
                [
                    {
                        "components": {
                            "headers": {header_name: header_data},
                            "schemas": {schema_name: schema_data},
                        },
                    },
                    OasBuilder.data,
                ]
            ),
        )

    def request_body(
        self,
        path: str,
        method: Literal[
            "get",
            "post",
            "put",
            "patch",
            "delete",
            "head",
            "options",
            "trace",
            "*",
        ],
        schema: Any,
        content_type: str = None,
        **kwargs
    ):
        """
        request_body [summary]

        [extended_summary]

        Args:
            path (str): [description]
            method (Literal[): [description]
            schema (Any): [description]
            content_type (str, optional): [description]. Defaults to None.
        """
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
        """

        Args:
          path: str:
          method: Literal["get":
          "post":
          "put":
          "patch":
          "delete":
          "head":
          "options":
          "trace"]:
          schema: Any:
          code: Union[int:
          str]:  (Default value = "default")
          content_type: str:  (Default value = None)
          description: str:  (Default value = "")

        Returns:

        """
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
                                                content_type: {
                                                    "schema": schema,
                                                }
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
        """

        Args:
          path: str:
          method: Literal["get":
          "post":
          "put":
          "patch":
          "delete":
          "head":
          "options":
          "trace"]:
          security: str:
          scopes:  (Default value = [])
          AND:  (Default value = False)
          OR:  (Default value = False)

        Returns:

        """
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
        """

        Args:
          path: str:
          method: Literal["get":
          "post":
          "put":
          "patch":
          "delete":
          "head":
          "options":
          "trace"]:
          in_:
          name:
          schema:
          description:
          **kwargs:

        Returns:

        """

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
        """

        Args:
          path: str:
          summary:  (Default value = "")
          description:  (Default value = "")
          servers:  (Default value = [])

        Returns:

        """
        path_data = OasBuilder.data.setdefault("paths", {}).setdefault(path, {})
        if summary:
            path_data["summary"] = summary
        if description:
            path_data["description"] = description
        if servers:
            path_data["servers"] = servers
        OasBuilder.data["paths"][path] = path_data


oas_builder = OasBuilder()
