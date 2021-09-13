from apispec import BasePlugin
from .resolver import Resolver


class SchemaQualPlugin(BasePlugin):
    def __init__(
        self,
    ):
        super().__init__()
        self.spec = None

    def init_spec(self, spec):
        super().init_spec(spec)
        self.spec = spec
        self.openapi_version = spec.openapi_version
        self.resolver = Resolver(openapi_version=self.openapi_version)

    def schema_helper(self, name, _, schema=None, **kwargs):
        self.resolver.resolve_schema(schema)

    def parameter_helper(self, parameter, **kwargs):
        # In OpenAPIv3, this only works when using the complex form using "content"
        self.resolver.resolve_schema(parameter)
        return parameter

    def response_helper(self, response, **kwargs):
        """Response component helper that allows using a marshmallow
        :class:`Schema <marshmallow.Schema>` in response definition.

        :param dict parameter: response fields. May contain a marshmallow
            Schema class or instance.
        """
        self.resolver.resolve_response(response)
        return response

    def operation_helper(self, path=None, operations={}, **kwargs):
        self.resolver.resolve_operations(operations)
