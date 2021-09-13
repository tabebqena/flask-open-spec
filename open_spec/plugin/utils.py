import importlib
from inspect import getmodule, isclass, isfunction
from pprint import pprint
import sys
from typing import Callable, cast
import typing
import marshmallow
from marshmallow import class_registry

from deepdiff import DeepDiff


def _import_module(mod: str):
    return importlib.import_module(mod)


def import_by_path(qualname):
    name = qualname.split(".")[-1]
    path = ".".join(qualname.split(".")[:-1])
    module = _import_module(path)
    obj = getattr(module, name)
    return obj


def resolve_schema_instance(schema, **kwargs):
    """Return schema instance for given schema (instance or class).

    :param type|Schema|str schema: instance, class or class name of marshmallow.Schema
    :return: schema instance of given schema (instance or class)
    """
    if isinstance(schema, str) and "." in schema:
        schema = import_by_path(schema)
    if isinstance(schema, type) and issubclass(schema, marshmallow.Schema):
        return schema(**kwargs)
    if isinstance(schema, marshmallow.Schema):
        return schema
    return class_registry.get_class(schema)(**kwargs)


def get_name(obj, module):
    name = getattr(obj, "__name__", None)
    if name:
        return name
    modules = [module]
    for m in modules:

        for name, o in m.__dict__.items():
            if not getattr(o, "__class__", None) or getattr(
                o, "__class__", None
            ) != getattr(obj, "__class__", None):
                continue
            if DeepDiff(o, obj):
                continue
                # if o == obj:
            return name


def get_schema_info(schema, **kwargs) -> dict:
    """resolve class name, module and properties of passed schema"""
    qualname = None
    module = None
    instance = None
    orig_schema = None
    if isinstance(schema, dict):
        return {
            "instance": schema,
            "qualname": None,
            "kwargs": {},
        }

    if isinstance(schema, str):
        orig_schema = schema
        schema = resolve_schema_instance(schema, **kwargs)
    #
    is_klass = isclass(schema)  # True in class schema,
    is_function = isfunction(schema)  # False in class Schema
    is_instance = isinstance(schema, marshmallow.Schema)
    #
    if is_klass and issubclass(schema, marshmallow.Schema):
        module = getmodule(schema)
        if orig_schema:
            name = orig_schema
            qualname = (
                getattr(schema, "__module__", "")
                + "."
                + orig_schema.split(".")[-1]
            )
        else:
            name = get_name(schema, module=module)
            if name:
                qualname = getattr(schema, "__module__", "") + "." + name
            else:
                qualname = None
        # file_ = getattr(module, "__file__", None)

        # name = orig_schema or getattr(schema, "__name__", None)
        instance = schema(**kwargs)
        return {
            "name": name,
            "qualname": qualname,
            "instance": instance,
            # "file": file_,
            "kwargs": {},
        }
    elif is_instance:
        # schema = schema  # cast(marshmallow.Schema, schema)

        if orig_schema:
            name = orig_schema
            qualname = (
                getattr(schema, "__module__", "")
                + "."
                + orig_schema.split(".")[-1]
            )
        else:
            module = getmodule(schema)
            name = get_name(schema, module=module)

            if name:
                qualname = getattr(schema, "__module__", "") + "." + name
            else:
                qualname = None
        # pprint(sys.modules)
        # file_ = getattr(module, "__file__", None)

        return {
            "name": name,
            "qualname": qualname,
            "instance": schema,
            "kwargs": {
                "dump_only": schema.dump_only,
                "exclude": schema.exclude,
                "load_only": schema.load_only,
                "many": schema.many,
                "only": schema.only,
                "ordered": schema.ordered,
                "partial": schema.partial,
                "unknown": schema.unknown,
            },
        }
    elif is_function:
        module = getmodule(schema)
        if orig_schema:
            name = orig_schema
            qualname = (
                getattr(schema, "__module__", "")
                + "."
                + orig_schema.split(".")[-1]
            )
        else:
            name = get_name(schema, module=module)
            if name:
                qualname = getattr(schema, "__module__", "") + "." + name
            else:
                qualname = None

        # file_ = getattr(module, "__file__", None)
        instance = cast(Callable, schema)(**kwargs)
        return {
            "name": name,
            "qualname": qualname,
            # "file": file_,
            "kwargs": kwargs,
            "instance": instance,
        }
    raise RuntimeError(f"Can't get schema info {schema}")
