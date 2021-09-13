from http.client import responses
from .utils import get_schema_info


class Resolver:
    def __init__(self, openapi_version):
        self.openapi_version = openapi_version

    def resolve_parameters(self, parameters):
        """
        Example: ::

        :param list parameters: the list of OpenAPI parameter objects to resolve.
        """
        resolved = []
        for parameter in parameters:
            if isinstance(parameter, dict) and not parameter.get(
                "x-schema", None
            ):

                if isinstance(parameter.get("schema", {}), dict):
                    resolved.append(parameter)
                elif isinstance(parameter.get("schema", {}), str):
                    info = get_schema_info(
                        parameter.get("schema", ""),
                        **parameter.get("x-schema-kwargs", {}),
                    )
                    parameter["x-schema"] = info["qualname"]
                    parameter["schema"] = info["instance"]

                    resolved.append(parameter)
                else:
                    self.resolve_schema(parameter)
                    resolved.append(parameter)
            else:
                resolved.append(parameter)
        return resolved

    def resolve_schema(self, data):
        """
        OpenAPIv3 Components: ::


        :param dict|str data: either a parameter or response dictionary that may
            contain a schema, or a reference provided as string
        """
        if not isinstance(data, dict):
            return

        # OAS 2 component or OAS 3 header

        if "schema" in data and not data.get("x-schema", None):

            if (
                isinstance(data.get("schema", None), dict)
                or data.get("schema", None) is None
            ):
                # data["x-schema"] = info["qualname"]
                # data["schema"] = info["instance"]
                pass

            else:
                info = get_schema_info(
                    data.get("schema", ""), **data.get("x-schema-kwargs", {})
                )
                data["x-schema"] = info["qualname"]
                data["schema"] = info["instance"]

        # OAS 3 component except header
        if self.openapi_version.major >= 3:
            if "content" in data:
                for content in data["content"].values():
                    if "schema" in content and not content.get(
                        "x-schema", None
                    ):
                        if (
                            isinstance(content.get("schema", None), dict)
                            or content.get("schema", None) is None
                        ):
                            pass
                        else:
                            info = get_schema_info(
                                content.get("schema", ""),
                                **content.get("x-schema-kwargs", {}),
                            )
                            content["x-schema"] = info["qualname"]
                            content["schema"] = info["instance"]
        # component schemas/schema

    def resolve_callback(self, callbacks):
        """Resolve marshmallow Schemas in a dict mapping callback name to OpenApi `Callback Object
        https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#callbackObject`_.

        This is done recursively, so it is possible to define callbacks in your callbacks.


        """
        for callback in callbacks.values():
            if isinstance(callback, dict):
                for path in callback.values():
                    self.resolve_operations(path)

    def resolve_response(self, response):
        """Resolve marshmallow Schemas in OpenAPI `Response Objects
        <https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#responseObject>`_.
        Schemas may appear in either a Media Type Object or a Header Object.


        :param dict response: the response object to resolve.
        """
        self.resolve_schema(response)

        if "headers" in response:
            for header in response["headers"].values():
                self.resolve_schema(header)

    def resolve_operations(self, operations, **kwargs):
        for operation in operations.values():
            if not isinstance(operation, dict):
                continue
            if "parameters" in operation:
                operation["parameters"] = self.resolve_parameters(
                    operation["parameters"]
                )
            if self.openapi_version.major >= 3:
                self.resolve_callback(operation.get("callbacks", {}))
                if "requestBody" in operation:
                    self.resolve_schema(operation["requestBody"])
            for response in operation.get("responses", {}).values():
                self.resolve_response(response)

        return operations
