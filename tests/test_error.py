import enum
from typing import Any, Generic, List, Optional, TypeVar, cast

from graphql import graphql_sync
from graphql.type import GraphQLSchema

from typed_graphql import TypedGraphqlMiddlewareManager
from typed_graphql import graphql_type


def get(field: str, data, info) -> Optional[Any]:
    return data.get(field)


def strict_get(field: str, data, info) -> Any:
    return data[field]


class MyEnum(enum.Enum):
    ABC = "abc"


def test_missing_type():
    X = TypeVar("X")

    class Paged(Generic[X]):
        def resolve_my_value(self, info) -> List[X]:
            return cast(List[X], ["z"])

    class User(Paged[str]):
        def resolve_xxx(self, info, data) -> MyEnum:
            return MyEnum.ABC

    class Query:
        def resolve_user(self, info) -> List[User]:
            return [User()]

    try:
        # Building a schema resolves all thunks, surfacing type errors in nested types
        GraphQLSchema(query=graphql_type(Query))
    except TypeError as e:
        # graphql-core wraps thunk exceptions in TypeError; unwrap to check cause
        cause = e.__cause__
        assert (
            cause.name
            == "Type '<class 'inspect._empty'>' for 'data' of User.resolve_xxx can not be converted to a GraphQL type"
        )
    else:
        raise Exception()
