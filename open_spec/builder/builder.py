from copy import deepcopy
from typing import Any, Literal, Optional, Union, cast

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from marshmallow import Schema

from .._parameters import VALID_METHODS_OPENAPI_V3
from .._utils import clean_parameters_list, merge_recursive
from ..plugin.plugin import SchemaQualPlugin
from ..decorators import Deferred
from .builder_resolver import (
    ComponentResolver,
    load_data as load_input_data,
    load_deferred_data,
)
from .utils import (
    _add_schema_to_components,
    _validate,
)


class OasBuilder:
    """
    Builder class to create the open api specifications at runtime.
    The generated spec will be loaded by the `OpenSpec` object.
    """

    def __init__(
        self,
        data: dict = {},
        default_required=True,
        default_content_type="application/json",
        allowed_methods=VALID_METHODS_OPENAPI_V3,
        #    deferred: List = [],
    ) -> None:
        self.input_data = deepcopy(data)
        self.data = deepcopy(data)
        self.default_required = default_required
        self.default_content_type = default_content_type
        self.allowed_methods = allowed_methods + ["*"]
        self.deferred_data = {}

        self.apispec = APISpec(
            data.get("info", {}).get("title", "") or "title",
            data.get("info", {}).get("version", "") or "1",
            "3.0.2",
            plugins=[SchemaQualPlugin(), MarshmallowPlugin()],
        )
        self.components_resolver = ComponentResolver(
            self.apispec, self.data, self.allowed_methods
        )

        load_input_data(self)
        self.load_deferred()
        load_deferred_data(self, self.deferred_data)

    def load_deferred(self):
        for attr_name, args, kwargs in Deferred._deferred:
            m = getattr(self, attr_name, None)
            if m:
                m(*args, **kwargs)
            else:
                raise ValueError(f"OasBuilder has no method named {attr_name}")

    def api_info(
        self,
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
        self.data = cast(
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
                    self.data,
                ]
            ),
        )

    def api_external_docs(self, url, description=""):
        """
        Add/edit externalDocs section of the api

        Args:
          url: url to the external docs
          description:  (Default value = "")

        Returns:

        """
        self.data = cast(
            dict,
            merge_recursive(
                [
                    {
                        "externalDocs": {
                            "url": url,
                            "description": description,
                        }
                    },
                    self.data,
                ]
            ),
        )

    def api_tag(self, name, description="", external_docs_url=""):
        """
        Add tag to the tags section of the api.

        Args:
          name: tag name
          description:  (Default value = "")
          external_docs_url:  (Default value = "")

        Returns:

        Examples:

        >>> OasBuilder.tag("MyTag")
        >>> print( self.data["tags"] )
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
        for t in self.apispec._tags:
            tname = t.get("name", "")
            if tname and tname == name:
                self.apispec._tags.remove(t)

        self.apispec.tag(tag=tag)

    def api_server(self, url, description):
        """
        Add server to the servers section of the api

        Args:
          url: server url
          description: server description

        Returns:

        Examples:

        >>> OasBuilder.server("http://spec.host.com", "spec server")
        >>> print( self.data["servers"] )
        [{"url": "http://spec.host.com", "description": "spec server"}]

        """
        _servers = self.data.get("servers", [])
        for sr in _servers:
            _url = sr.get("url", "")
            if _url and _url == url:
                _servers.remove(sr)
        self.data["servers"] = _servers
        self.data = cast(
            dict,
            merge_recursive(
                [
                    {"servers": [{"url": url, "description": description}]},
                    self.data,
                ]
            ),
        )

    def api_security_scheme(self, name: str, security: dict):
        """
        api_key_security_schema generate apiKey authentivation schema and storing it in the api components

        Args:
          name: str:  arbitrary name for the security scheme

        Returns: None

        Examples:

        >>> OasBuilder.basic_security_schema("basicAuth")
        >>> print(self.data["components"]["securitySchemes"])
        >>> {""basicAuth"": {"type": "http", "scheme": "basic"}}

        Note: The securitySchemes section alone is not enough; you must also use security for the API key to have effect.
        security can also be set on the operation level instead of globally.

        security:
        - basicAuth: []

        """
        self.apispec.components.security_scheme(name, security)

    def component_schema(self, schema, schema_kwargs={}):
        _validate(None, None, schema, self.allowed_methods)

        name, schema_data = self.components_resolver._component_schema(
            schema, schema_kwargs
        )
        _add_schema_to_components(self.apispec, name, schema_data)
        """self.apispec.components.schema(schema_name, schema_data)

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
        "self.data = cast(
            dict,
            merge_recursive(
                [
                    {"components": {"schemas": {name: schema_data}}},
                    self.data,
                ]
            ),
        )"
        self.apispec.components.schema(name, schema_data)
        """
        return name

    def component_response(
        self,
        schema: Any,
        response_name: Optional[str],
        content_type: str,
        description: str = "",
        schema_kwargs={},
    ):
        _validate(None, None, schema, self.allowed_methods)
        self.components_resolver.resolve_responses(
            {
                "components": {
                    "responses": {
                        response_name: {
                            "content": {
                                content_type: {
                                    "schema": schema,
                                    "x-schema-kwargs": schema_kwargs,
                                }
                            },
                            "description": description,
                        }
                    }
                }
            }
        )
        return
        # delete this after full testing

        response, schemas = self.components_resolver._component_response(
            {
                "content": {
                    content_type: {
                        "schema": schema,
                        "x-schema-kwargs": schema_kwargs,
                    }
                },
                "description": description,
            },
        )

        schema_name = list(schemas.keys())[0]
        schema_data = schemas.get(schema_name)
        _add_schema_to_components(self.apispec, schema_name, schema_data)  # type: ignore

        self.data = cast(
            dict,
            merge_recursive(
                [
                    {
                        "components": {
                            "responses": {response_name: response},
                        },
                    },
                    self.data,
                ],
            ),
        )

    def component_request_body(
        self, request_body_name: str, content_type: str, schema: Any, **kwargs
    ):
        _validate(None, None, schema, self.allowed_methods)
        self.components_resolver.resolve_request_bodies(
            {
                "components": {
                    "requestBodies": {
                        request_body_name: {
                            "content": {
                                content_type: {
                                    "schema": schema,
                                }
                            },
                        }
                    }
                }
            }
        )
        return
        spec = APISpec("title", "1", "3.0.2", plugins=[MarshmallowPlugin()])
        spec.path(
            "/invalid",
            operations={
                "post": {
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
            .get("post", {})
            .get("requestBody", {})
        )
        schemas = dict_.get("components", {}).get("schemas", {})
        schema_name = list(schemas.keys())[0]
        schema_data = (
            dict_.get("components", {}).get("schemas", {}).get(schema_name)
        )

        self.data = cast(
            dict,
            merge_recursive(
                [
                    {
                        "components": {
                            "requestBodies": {request_body_name: body_data},
                            "schemas": {schema_name: schema_data},
                        },
                    },
                    self.data,
                ]
            ),
        )

        # self.data["paths"][path][mthd]["requestBody"] = request_body

    def component_parameter(
        self, parameter_name, in_, name, schema, description="", **kwargs
    ):
        _validate(None, None, schema, self.allowed_methods)

        required = kwargs.get("required", False)
        self.components_resolver.resolve_parameters(
            {
                "components": {
                    "parameters": {
                        parameter_name: {
                            "in": in_,
                            "name": name,
                            "schema": schema,
                            "description": description,
                            "required": required,
                            **kwargs,
                        }
                    }
                }
            }
        )
        return
        # delete after full testing

        param = {
            "in": in_,
            "name": name,
            "schema": schema,
            "description": description,
            "required": required,
            **kwargs,
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

        self.data = cast(
            dict,
            merge_recursive(
                [
                    {
                        "components": {
                            "parameters": {parameter_name: param_data},
                            #     "schemas": {schema_name: schema_data},
                        },
                    },
                    self.data,
                ]
            ),
        )

    def component_header(self, header_name, schema, description="", **kwargs):
        _validate(None, None, schema, self.allowed_methods)
        self.components_resolver.resolve_headers(
            {
                "components": {
                    "headers": {
                        header_name: {
                            "schema": schema,
                            "description": description,
                            **kwargs,
                        },
                    },
                }
            }
        )

    @staticmethod
    def ref_to_schema(schema: Union[str, Schema]):
        ref = {}
        if isinstance(schema, str):
            return {"$ref": f"#/components/schemas/{schema}"}
        spec = APISpec("title", "1", "3.0.2", plugins=[MarshmallowPlugin()])
        # spec.components.schema()

    def path_request_body(
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
        **kwargs,
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
        _validate(path, mthd, schema, self.allowed_methods)
        self.deferred_data = cast(
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
                    self.deferred_data,
                ]
            ),
        )
        # self.data["paths"][path][mthd]["requestBody"] = request_body

    def path_response(
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
        _validate(path, mthd, schema, self.allowed_methods)
        content_type = content_type or self.default_content_type
        self.deferred_data = cast(
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
                    self.deferred_data,
                ]
            ),
        )

    def _set_security_requirements(
        self, old, security: str, scopes=[], AND=False, OR=True, index=-1
    ):
        if old and AND:
            old[index].update({security: scopes})
            # self.deferred_data["paths"][path]["security"] = sec

        elif old and OR:
            if index == -1:
                index = len(old)
            cast(list, old).insert(index, {security: scopes})
            # old = old + [{security: scopes}]  # type: ignore
            # self.deferred_data["paths"][path]["security"] = sec
        else:
            old = [{security: scopes}]
        return old

    def path_security_requirements(
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
        security: str,
        scopes=[],
        AND=False,
        OR=True,
        index=-1,
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
          "trace",
          "*"]:
          security: str:
          scopes:  (Default value = [])
          AND:  (Default value = False)
          OR:  (Default value = False)

        Returns:

        """
        """
        path = None,

        """
        if method:
            method = method.lower()  # type: ignore
        _validate(path, method, None, self.allowed_methods)
        if AND and OR:
            raise ValueError("You should specify only one of AND/OR not both")
        methods = [method.lower()]
        if method == "*":
            methods = self.allowed_methods
        for m in methods:
            if m == "*":
                continue
            old = (
                self.data.setdefault("paths", {})
                .setdefault(path, {})
                .setdefault(m, {})
                .get("security", [])
            )
            self.data["paths"][path][method][
                "security"
            ] = self._set_security_requirements(
                old, security, scopes, AND, OR, index
            )

    def root_security_requirements(
        self,
        security: str,
        scopes=[],
        AND=False,
        OR=True,
        index=-1,
    ):
        """

        Args:
          security: str:
          scopes:  (Default value = [])
          AND:  (Default value = False)
          OR:  (Default value = False)

        Returns:

        """
        _validate(None, None, None, self.allowed_methods)
        if AND and OR:
            raise ValueError("You should specify only one of AND/OR not both")

        old = self.data.setdefault("security", [])
        self.data["security"] = self._set_security_requirements(
            old, security, scopes, AND, OR, index
        )

    def path_parameter(
        self,
        path: str,
        in_,
        name,
        schema,
        description,
        **kwargs,
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

        # mthd = method.lower()
        _validate(path, None, schema, self.allowed_methods)
        required = kwargs.get("required", self.default_required)

        parameters = self.data.get("paths", {}).get(path, {}).get(
            "parameters", []
        ) + self.deferred_data.get("paths", {}).get(path, {}).get(
            "parameters", []
        )
        param = {
            "in": in_,
            "name": name,
            "schema": schema,
            "description": description,
            "required": required,
        }
        parameters.append(param)
        parameters = clean_parameters_list(parameters)

        self.deferred_data.setdefault("paths", {}).setdefault(
            path, {}
        ).setdefault("parameters", parameters)

    def path_details(self, path: str, summary="", description="", servers=[]):
        """

        Args:
          path: str:
          summary:  (Default value = "")
          description:  (Default value = "")
          servers:  (Default value = [])

        Returns:

        """

        path_data = self.data.setdefault("paths", {}).setdefault(path, {})
        if summary:
            path_data["summary"] = summary
        if description:
            path_data["description"] = description
        if servers:
            path_data["servers"] = servers
        self.data["paths"][path] = path_data

    def get_data(self) -> dict:
        data = deepcopy(self.data)
        spec_data = deepcopy(self.apispec.to_dict())
        input_data = deepcopy(self.input_data)
        if "servers" in input_data:
            del input_data["servers"]
        ret = cast(
            dict,
            merge_recursive(
                [
                    data,
                    spec_data,
                ]
            ),
        )
        return ret
