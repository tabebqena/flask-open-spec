import os
from typing import Dict, List
import functools
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
