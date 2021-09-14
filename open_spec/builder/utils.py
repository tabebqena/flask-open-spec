
import apispec

from apispec import APISpec

from .._parameters import VALID_METHODS_OPENAPI_V3
from ..plugin import get_schema_info


from apispec import APISpec
from ..plugin.utils import get_schema_info


def _add_schema_to_components(apispec: APISpec, name, schema: dict, suffix=0):
    names = apispec.components.schemas.keys()
    _name = name
    if suffix:
        _name = name + str(suffix)
    if not _name in names:
        apispec.components.schema(_name, schema)
        return _name
    qual = None
    kwargs = {}
    prev_schema = {}
    prev_qual = None
    prev_kwargs = {}
    if schema:
        qual = schema.get("x-schema", None)
        kwargs = schema.get("x-schema-kwargs", {})
        prev_schema = apispec.components.schemas[_name]
        prev_qual = prev_schema.get("x-schema", None)
        prev_kwargs = prev_schema.get("x-schema-kwargs", {})
    if not qual or not prev_qual:
        # Todo
        apispec.components.schema(_name, schema)
        return _name
    if qual == prev_qual and kwargs == prev_kwargs:
        return _name
    return _add_schema_to_components(apispec, name, schema, suffix + 1)


def _validate(path, method, schema, allowed_methods=VALID_METHODS_OPENAPI_V3):
    # allowed_methods = VALID_METHODS_OPENAPI_V3 + ["*"]
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
        try:
            get_schema_info(schema)
        except Exception as e:
            print(e)
            raise schema_error
