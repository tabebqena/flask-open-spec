from inspect import getmodule, isclass, isfunction
import os
from typing import Dict, List, cast
import functools
import marshmallow
import yaml
from apispec.yaml_utils import dict_to_yaml
import ntpath


def merge_recursive(values):
    return functools.reduce(_merge_recursive, values, {})


def _merge_recursive(child, parent):
    if isinstance(child, dict) and not parent:
        parent = {}
    if isinstance(parent, dict) and not child:
        child = {}
    if isinstance(child, list) and not parent:
        parent = []
    if isinstance(parent, list) and not child:
        child = []

    if isinstance(child, dict) and isinstance(parent, dict):
        child = child or {}
        parent = parent or {}
        keys = set(child.keys()).union(parent.keys())
        return {
            key: _merge_recursive(child.get(key), parent.get(key))
            for key in keys
        }
    elif isinstance(child, list) and isinstance(parent, list):
        merged = parent
        for item in child:
            if item not in merged:
                merged.append(item)
        return [_merge_recursive(x, None) for x in merged]
    return child if child is not None else parent


ALLOW_NULL = ["security"]
ALLOW_EMPTY = ["security", "responses"]


def remove_none(obj, key=None, allow=[]):
    if key in ALLOW_NULL or key in allow:
        return obj
    if isinstance(obj, (list, tuple, set)):
        return type(obj)(remove_none(x) for x in obj if x is not None)
    elif isinstance(obj, dict):
        return type(obj)(
            (remove_none(k, key=k), remove_none(v, key=k))
            for k, v in obj.items()
            if k is not None and v is not None
        )
    else:
        return obj


def remove_empty(obj, key=None):
    if key in ALLOW_EMPTY:
        return obj
    if isinstance(obj, (list, tuple, set)):
        return (
            type(obj)(
                remove_empty(x) for x in obj if x and x not in ALLOW_EMPTY
            )
            or None
        )
    elif isinstance(obj, dict):
        res = {}
        for k, v in obj.items():
            if k in ALLOW_EMPTY:
                res[k] = v
            else:
                res[k] = remove_empty(v, key=k)
        return res or None
    else:
        if obj:
            return obj
        else:
            return None


def clean_data(data):
    cycles = 10
    count = 0
    while count < cycles:
        data = remove_empty(remove_none(remove_empty(data)))
        count += 1
    return data


def clean_parameters_list(params: List[Dict]) -> List[Dict]:
    """
    clean_parameters_list [summary]

    [extended_summary]

    :param params: [description]
    :type params: List[Dict]
    """
    res: List[Dict] = []
    for param in params:
        name = param.get("name")
        location = param.get("in")
        prev = [
            x for x in res if x.get("name") == name and x.get("in") == location
        ]
        if len(prev) == 0:
            res.append(param)
    return res


def load_file(path, default={}):
    data = default
    if os.path.exists(path):
        with open(path) as f:
            data = yaml.safe_load(f) or default
    if not data:
        return default
    return data


def yaml_dump(intro="", data={}, file=None):
    yaml.Dumper.ignore_aliases = lambda self, data: True
    with open(file, "w") as f:
        f.write(intro)
        dict_to_yaml(data, {"stream": f, "sort_keys": False})


def cache_file(path, oas_dir, cache_dir):
    if not os.path.exists(path):
        return
    rel_path = os.path.relpath(path, oas_dir)
    dir = os.path.dirname(rel_path)
    fname = ntpath.basename(path).split(".")[0]
    ext = os.path.splitext(path)[1]
    count = 1
    while True:
        new_path = os.path.join(cache_dir, dir, fname + "_" + str(count) + ext)
        if not os.path.exists(new_path):
            break
        count += 1
    try:
        os.makedirs(os.path.dirname(new_path))
    except Exception as e:
        pass

    with open(new_path, "w") as f:

        f.write(open(path).read())
    return new_path


def get_schema_info(schema, **kwargs):
    # depercated as there is many synamiic features  of schema
    # https://marshmallow.readthedocs.io/en/stable/custom_fields.html

    """resolve class name, module and properties of passed schema"""
    qualname = None
    module = None
    info = {}
    """
    is_klass: 
    True in calss GistSchema(schema.Schema)
    False in GistSchema(any args)
    False in schema=GistSchema(anyargs)
    True in schema.Schema.from_dict(dict here)
    Fals e in function returning class ex:. get_class without()
    """
    is_klass = isclass(schema)  # True in class schema,
    """
    is_sub_klass: 
    True calss GistSchema(schema.Schema)
    False in GistSchema(any args)
    False in schema=GistSchema(anyargs)
    True in schema.Schema.from_dict(dict here)
    Fals e in function returning class ex:. get_class without()

    """
    is_sub_klass = False
    if is_klass:
        is_sub_klass = issubclass(
            schema, marshmallow.Schema
        )  # True in class Schema,
    """
    is_function: 
    False in calss GistSchema(schema.Schema)
    False in GistSchema(any args)
    False in schema=GistSchema(anyargs)
    False in schema.Schema.from_dict(dict here)

    True in function returning class ex:. get_class without()

    """
    is_function = isfunction(schema)  # False in class Schema
    """
    is_instance: 
    False in calss GistSchema(schema.Schema)
    True in GistSchema(any args)
    True in schema=GistSchema(anyargs)
    False in schema.Schema.from_dict(dict here)
    False in function returning class ex:. get_class without()

    """
    is_instance = isinstance(
        schema, marshmallow.Schema
    )  # TRue in schema class call  False in class schema
    print("is_klass: ", is_klass)
    print("is_sub_klass: ", is_sub_klass)
    print("is_function: ", is_function)
    print("is_instance: ", is_instance)
    if is_sub_klass:
        qualname = getattr(schema, "__module__", None)
        module = getmodule(schema)
        file_ = getattr(module, "__file__", None)

        name = getattr(schema, "__name__", None)
        # print(getmodule(schema).__)
        return {"name": name, "qualname": qualname, "file": file_, "kwargs": {}}
    elif is_instance:
        schema = cast(marshmallow.Schema, schema)
        klass = schema.__class__
        info = get_schema_info(klass)
        info["kwargs"].update(
            {
                "dump_only": schema.dump_only,
                "exclude": schema.exclude,
                "load_only": schema.load_only,
                "many": schema.many,
                "only": schema.only,
                "ordered": schema.ordered,
                "partial": schema.partial,
                "unknown": schema.unknown,
            }
        )
        return info
    elif is_function:
        qualname = getattr(schema, "__module__", None)
        module = getmodule(schema)
        file_ = getattr(module, "__file__", None)

        name = getattr(schema, "__name__", None)
        return {"name": name, "qualname": qualname, "file": file_, "kwargs": {}}
