from typing import Generic, TypeVar, cast

from typed_graphql.util import get_arg_for_typevar


def test_get_arg_for_typevar():
    X = TypeVar('X')

    class Node(Generic[X]):
        def my_value(self, info) -> X:
            return cast(X, "z")

    class User(Node[str]):
        pass

    u = User()

    assert get_arg_for_typevar(u.my_value.__annotations__["return"], User) == str
