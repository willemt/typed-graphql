from dataclasses import dataclass
from typing import Any
from typing import List
from typing import NewType
from typing import Optional
from typing import Set

from graphql import graphql_sync
from graphql.type import GraphQLSchema

from typed_graphql import TypedGraphqlMiddlewareManager
from typed_graphql import graphql_type


def get(field: str, data, info) -> Optional[Any]:
    return data.get(field)


def strict_get(field: str, data, info) -> Any:
    return data[field]


Animal = NewType("Animal", str)


def test_dataclass_with_set():
    @dataclass
    class User:
        value: Set[Animal]

    class Query:
        def resolve_user(self, info) -> List[User]:
            return [User({Animal("cat"), Animal("dog")})]

    assert str(graphql_type(Query).fields["user"].type) == "[User!]!"
    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(
        schema, "{user { value }}", Query(), middleware=TypedGraphqlMiddlewareManager()
    )
    assert sorted(result.data["user"][0]["value"]) == sorted(["dog", "cat"])
    assert result.errors is None


def test_dataclass_with_set_alias():
    @dataclass
    class User:
        value: set[Animal]

    class Query:
        def resolve_user(self, info) -> List[User]:
            return [User({Animal("cat"), Animal("dog")})]

    assert str(graphql_type(Query).fields["user"].type) == "[User!]!"
    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(
        schema, "{user { value }}", Query(), middleware=TypedGraphqlMiddlewareManager()
    )
    assert sorted(result.data["user"][0]["value"]) == sorted(["dog", "cat"])
    assert result.errors is None
