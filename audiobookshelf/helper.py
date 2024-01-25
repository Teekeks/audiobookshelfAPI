
def camel(snake: str) -> str:
    first, *others = snake.split('_')
    return ''.join([first.lower(), *map(str.title, others)])


def remove_none_values(d: dict) -> dict:
    """Removes items where the value is None from the dict.
    This returns a new dict and does not manipulate the one given.

    :param d: the dict from which the None values should be removed"""
    return {k: v for k, v in d.items() if v is not None}
