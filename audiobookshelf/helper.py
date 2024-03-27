import urllib.parse
from enum import Enum


def camel(snake: str) -> str:
    first, *others = snake.split('_')
    return ''.join([first.lower(), *map(str.title, others)])


def remove_none_values(d: dict) -> dict:
    """Removes items where the value is None from the dict.
    This returns a new dict and does not manipulate the one given.

    :param d: the dict from which the None values should be removed"""
    return {k: v for k, v in d.items() if v is not None}


def build_url(url: str, params: dict) -> str:
    """Build a valid url string

    :param url: base URL
    :param params: dictionary of URL parameter
    :return: URL
    """

    def get_val(val):
        if isinstance(val, Enum):
            return str(val.value)
        return str(val)

    def add_param(res, k, v):
        if len(res) > 0:
            res += "&"
        res += str(k)
        if v is not None:
            res += "=" + urllib.parse.quote(get_val(v))
        return res

    result = ""
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, list):
            for va in value:
                result = add_param(result, key, va)
        else:
            result = add_param(result, key, value)
    return url + (("?" + result) if len(result) > 0 else "")
