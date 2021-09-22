from copy import deepcopy
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

from .._parameters import VALID_METHODS_OPENAPI_V3
from ..plugin.plugin import SchemaQualPlugin
from apispec import APISpec
from typing import TYPE_CHECKING, Dict, cast
from .utils import _add_schema_to_components, _validate

if TYPE_CHECKING:
    from .builder import OasBuilder


class ComponentResolver:
    def __init__(
        self,
        apispec: APISpec,
        data: Dict = {},
        allowed_methods=VALID_METHODS_OPENAPI_V3,
    ) -> None:
        self.main_apispec = apispec
        self.row_data = data
        self.allowed_methods = allowed_methods

    def create_apispec(self):

        return APISpec(
            "title",
            "1",
            "3.0.2",
            plugins=[SchemaQualPlugin(), MarshmallowPlugin()],
        )

    def resolve_schemas(self, components_schemas: dict):
        """components_schemas = self.row_data.get("components", {}).get(
            "schemas", {}
        )"""
        for schema_name in list(components_schemas.keys()):
            kwargs = (
                self.row_data.get("components", {})
                .get("schemas-kwargs", {})
                .get(schema_name, {})
            )
            schema = components_schemas[schema_name]
            """if not kwargs and isinstance(schema, dict):
                kwargs = schema.get("schemas-kwargs", {})"""
            if isinstance(schema, dict):
                _add_schema_to_components(
                    self.main_apispec, schema_name, schema
                )
            else:
                self._component_schema(
                    schema,
                    kwargs,
                )
        for schema_name in list(components_schemas.keys()):
            del self.row_data["components"]["schemas"][schema_name]
            try:
                del self.row_data["components"]["schemas-kwargs"][schema_name]
            except:
                pass

    def _component_schema(self, schema, schema_kwargs={}):
        _validate(None, None, schema, self.allowed_methods)
        spec = self.create_apispec()

        """if isinstance(schema, dict):
            schema_kwargs = schema_kwargs or schema.get("schemas-kwargs", {})"""
        if isinstance(schema, dict):
            return None, schema

        spec.path(
            "/invalid",
            operations={
                "get": {
                    "responses": {
                        "default": {
                            "content": {
                                "application/json": {
                                    "schema": schema,
                                    "x-schema-kwargs": schema_kwargs,
                                },
                            }
                        }
                    }
                },
            },
        )
        #
        dict_ = spec.to_dict()
        self.__set_x_schema(
            dict_,
            dict_["paths"]["/invalid"]["get"]["responses"]["default"][
                "content"
            ]["application/json"],
        )

        names = list(dict_.get("components", {}).get("schemas", {}).keys())

        name = None
        if len(names) > 0:
            name = names[0]
        data = dict_.get("components", {}).get("schemas", {}).get(name, {})
        if name and data:
            _add_schema_to_components(self.main_apispec, name, data)

        return name, data

    def __set_x_schema(self, dict_: Dict, data):
        x_schema = data.get("x-schema")
        x_schema_kwargs = data.get("x-schema-kwargs")
        schema_ref: str = data.get("schema", {}).get("$ref", "")
        if schema_ref:
            del data["schema"]["$ref"]

        if x_schema:
            schema_name = schema_ref.split("/")[-1]
            schema_data = (
                dict_.get("components", {})
                .get("schemas", {})
                .get(schema_name, {})
            )
            if schema_data:
                dict_["components"]["schemas"][schema_name][
                    "x-schema"
                ] = x_schema
                if x_schema_kwargs:
                    dict_["components"]["schemas"][schema_name][
                        "x-schema-kwargs"
                    ] = x_schema_kwargs

    def __add_schema_ref(self, name: str, schema: Dict, data: dict):

        if schema.get("x-schema", None) == data.get("x-schema", None):
            data["schema"]["$ref"] = f"#/components/schemas/{name}"

    def resolve_responses(self, data: dict = {}):
        """components_responses = self.row_data.get("components", {}).get(
            "responses", {}
        )"""
        if not data:
            data = self.row_data

        for response_name, response in (
            data.get("components", {}).get("responses", {}).items()
        ):
            response_data, _ = self._component_response(response)
            self.main_apispec.components.response(response_name, response_data)

        if data.get("components", {}).get("responses", {}):
            for key in list(data["components"]["responses"].keys()):
                del data["components"]["responses"][key]

    def _component_response(self, response_data: dict):
        schema = response_data.get("schema", {})
        _validate(None, None, schema, self.allowed_methods)
        spec = self.create_apispec()
        spec.path(
            "/invalid",
            operations={
                "get": {"responses": {"default": response_data}},
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

        for media_type_data in response_data.get("content", {}).values():
            self.__set_x_schema(dict_, media_type_data)

        for schema_name, schema in (
            dict_.get("components", {}).get("schemas", {}).items()
        ):
            schema_name = _add_schema_to_components(
                self.main_apispec, schema_name, schema
            )
            for k in response_data.get("content", {}).keys():
                self.__add_schema_ref(
                    schema_name, schema, response_data["content"][k]
                )

        return response_data, dict_.get("components", {}).get("schemas", {})

    def resolve_request_bodies(self, data: dict = {}):
        if not data:
            data = self.row_data
        components_bodies = data.get("components", {}).get("requestBodies", {})
        for body_name, body in components_bodies.items():
            body_data, _ = self._component_request_body(body)
            self.row_data.setdefault("components", {}).setdefault(
                "requestBodies", {}
            )[body_name] = body_data

    def _component_request_body(self, body: dict):
        # schema: Any, content_type: str, request_body_name: str, **kwargs
        schema = body.get("schema", {})
        _validate(None, None, schema, self.allowed_methods)
        spec = self.create_apispec()
        spec.path(
            "/invalid",
            operations={
                "post": {"requestBody": body},
            },
        )
        dict_ = spec.to_dict()
        body_data = (
            dict_.get("paths", {})
            .get("/invalid", {})
            .get("post", {})
            .get("requestBody", {})
        )

        for media_type_data in body_data.get("content", {}).values():
            self.__set_x_schema(dict_, media_type_data)

        for schema_name, schema in (
            dict_.get("components", {}).get("schemas", {}).items()
        ):
            schema_name = _add_schema_to_components(
                self.main_apispec, schema_name, schema
            )
            for k in body_data.get("content", {}).keys():
                self.__add_schema_ref(
                    schema_name, schema, body_data["content"][k]
                )

        return body_data, dict_.get("components", {}).get("schemas", {})

    def resolve_parameters(self, data: dict = {}):
        parameters = {}
        if not data:
            data = self.row_data
        parameters = data.get("components", {}).get("parameters", {})
        keys = list(parameters.keys())
        for param_name in keys:
            parameter_data, schemas = self._component_parameter(
                parameters[param_name]
            )
            self.main_apispec.components.parameter(
                param_name, parameter_data.get("in", "path"), parameter_data
            )
            for schema_name, schema in schemas.items():
                if schema_name:
                    _add_schema_to_components(
                        self.main_apispec, schema_name, schema
                    )
        if data:
            for key in list(parameters.keys()):
                del data["components"]["parameters"][key]
        ####

    def _component_parameter(self, parameter):
        location = parameter.get("in", "path")
        kwargs = {}
        for k, v in parameter.items():
            if k in ["in", "name", "schema", "description", "required"]:
                continue
            kwargs[k] = v
        schema = parameter.get("schema", None)
        description = parameter.get("description", "")
        required = parameter.get("required", False)
        name = parameter.get("name", "")

        _validate(None, None, schema, self.allowed_methods)

        schema_name, schema_data = self._component_schema(schema, kwargs)
        if schema_name:
            schema_name = _add_schema_to_components(
                self.main_apispec, schema_name, schema_data
            )

        param = {
            "in": location,
            "name": name,
            "description": description,
            "required": required,
            **kwargs,
        }
        if schema_name:
            param["schema"] = {"$ref": f"#/components/schemas/{schema_name}"}
        else:
            param["schema"] = schema

        spec = self.create_apispec()
        spec.path("/invalid", operations={"get": {"parameters": [param]}})
        dict_ = spec.to_dict()
        param_data = (
            dict_.get("paths", {})
            .get("/invalid", {})
            .get("get", {})
            .get("parameters", [])[0]
        )
        return param_data, dict_.get("components", {}).get("schemas", {})

    def resolve_headers(self, data: Dict = {}):
        if not data:
            data = self.row_data

        for header_name, header in (
            data.get("components", {}).get("headers", {}).items()
        ):
            header_data, _ = self._component_header(header)
            self.main_apispec.components.header(header_name, header_data)

        if data.get("components", {}).get("headers", {}):
            for key in list(data["components"]["headers"].keys()):
                del data["components"]["headers"][key]

    def _component_header(self, header):
        schema = header.get("schema", {})
        _validate(None, None, schema, self.allowed_methods)
        spec = self.create_apispec()
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
                            "headers": {"header_name": header},
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
            .get("header_name", {})
        )

        self.__set_x_schema(dict_, header_data)

        for schema_name, schema in (
            dict_.get("components", {}).get("schemas", {}).items()
        ):
            schema_name = _add_schema_to_components(
                self.main_apispec, schema_name, schema
            )
            self.__add_schema_ref(schema_name, schema, header_data)

        return header_data, dict_.get("components", {}).get("schemas", {})


map_ = {
    "schemas": "schema",
    "responses": "response",
    # "requestBodies": "requestBody",
    "parameters": "parameter",
    "examples": "example",
    "headers": "header",
    "securitySchemes": "security_scheme",
    # "links":
    # callbacks
}


def load_components(
    oas_builder: "OasBuilder",
    row_data: dict,
    resolver: ComponentResolver,
    allowed_methods=VALID_METHODS_OPENAPI_V3,
):
    apispec = oas_builder.apispec
    extra_data = {}
    components = row_data.get("components", {})
    # schemas
    resolver.resolve_schemas(components.get("schemas", {}))
    # responses
    resolver.resolve_responses()
    # parameters
    resolver.resolve_parameters()
    # requestBodies
    # NOT implemented in apispec_components
    resolver.resolve_request_bodies()
    # headers
    resolver.resolve_headers()
    # securitySchemes
    components_sec_schemes = deepcopy(components.get("securitySchemes", {}))
    for scheme_name, scheme in components_sec_schemes.items():
        apispec.components.security_scheme(scheme_name, scheme)

    # examples
    components_examples = deepcopy(components.get("examples", {}))
    for example_name, example in components_examples.items():
        apispec.components.example(example_name, example)

    # rest
    # callbacks
    # "links":
    # "callbacks"
    for comp_type, comp_data in components.items():
        if comp_type in [
            "schemas",
            "schemas-kwargs",
            "responses",
            "requestBodies",
            "parameters",
            "securitySchemes",
            "examples",
        ]:
            continue
        method = getattr(apispec.components, map_.get(comp_type, ""))
        if method and comp_data:
            for item_id, item in comp_data.items():
                method(item_id, item)
    return extra_data


def load_tags(
    apispec: APISpec,
    row_data: dict,
    allowed_methods=VALID_METHODS_OPENAPI_V3,
):
    tags = row_data.get("tags", [])
    for t in tags:
        apispec.tag(t)
        row_data.get("tags", []).remove(t)


def _resolve_parameters(oas_builder: "OasBuilder", data: dict):
    _parameters = data.get("parameters", [])
    parameters = []
    for param in _parameters:
        schema = param.get("schema", None)
        if isinstance(schema, dict):
            parameter_data = param
            parameters.append(parameter_data)

        else:
            (
                parameter_data,
                schemas,
            ) = oas_builder.components_resolver._component_parameter(param)
            parameters.append(parameter_data)
            for schema_name, schema in schemas.items():
                _add_schema_to_components(
                    oas_builder.apispec, schema_name, schema
                )
    if parameters:
        data["parameters"] = parameters


def load_paths(
    oas_builder: "OasBuilder",
    row_data: dict,
    allowed_methods=VALID_METHODS_OPENAPI_V3,
):
    paths = row_data.get("paths", {})
    paths_keys = list(paths.keys())
    not_implemented_keys = ["servers"]
    not_implemented_data = {}

    for p in paths:
        path_data = row_data.get("paths", {}).get(p, {})
        summary = path_data.get("summary", "")
        description = path_data.get("description", "")
        _resolve_parameters(oas_builder, path_data)
        parameters = path_data.get("parameters", [])
        kwargs = {}
        for k, v in path_data.items():
            if (
                k not in ["summary", "description", "parameters"]
                and k not in not_implemented_keys
                and k.lower() not in allowed_methods
                and k.lower() not in VALID_METHODS_OPENAPI_V3
            ):
                kwargs[k] = v
            if k in not_implemented_keys:
                not_implemented_data.setdefault(p, {})[k] = path_data[k]

        operations = {}
        for m in allowed_methods:
            operation_data = cast(dict, path_data.get(m.lower(), {}))
            if operation_data:
                o_parameters = []
                _o_parameters = operation_data.pop("parameters", [])
                for o_param in _o_parameters:
                    (
                        o_parameter_data,
                        schemas,
                    ) = oas_builder.components_resolver._component_parameter(
                        o_param
                    )
                    o_parameters.append(o_parameter_data)
                    for schema_name, schema in schemas.items():
                        _add_schema_to_components(
                            oas_builder.apispec, schema_name, schema
                        )
                if _o_parameters:
                    operations["parameters"] = o_parameters

                operations[m.lower()] = operation_data
        oas_builder.apispec.path(
            p,
            summary=summary,
            description=description,
            parameters=parameters,
            operations=operations,
            kwargs=kwargs,
        )
        # data = oas_builder.apispec.to_dict()
        # oas_builder.components_resolver.resolve_schemas(data)
        # oas_builder.components_resolver.resolve_parameters(data)
        # oas_builder.components_resolver.resolve_request_bodies(data)
        # oas_builder.components_resolver.resolve_responses(data)
        # oas_builder.components_resolver.resolve_headers(data)

    for p in paths_keys:
        del paths[p]
    if not_implemented_data:
        for p in not_implemented_data:
            row_data.setdefault("paths", {}).setdefault(p, {}).update(
                not_implemented_data[p]
            )


def load_data(
    oas_builder: "OasBuilder",
):
    apispec = oas_builder.apispec
    row_data = oas_builder.data
    components_resolver = oas_builder.components_resolver
    allowed_methods = oas_builder.allowed_methods

    load_components(oas_builder, row_data, components_resolver, allowed_methods)
    load_paths(oas_builder, row_data, allowed_methods)
    load_tags(apispec, row_data, allowed_methods)


def load_deferred_data(oas_builder: "OasBuilder", data: dict = {}):
    allowed_methods = oas_builder.allowed_methods

    load_paths(oas_builder, data, allowed_methods)


"""info
servers
paths
components
security
tags
externalDocs"""
