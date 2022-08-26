from typing_inspect import is_typevar


def get_arg_for_typevar(typevar, generic):
    """Return the type of the TypeVar of this Generic"""

    assert is_typevar(typevar)

    # Search bases for the generic
    for base in generic.__orig_bases__:
        if base.__origin__.__orig_bases__[0].__args__[0] == typevar:
            return base.__args__[0]

    return None
