from typing import Any, Iterable, Optional

from graphql import graphql_sync
from graphql.type import GraphQLSchema

from typed_graphql import SimpleResolver, TypedGraphQLObject


def get(field: str, data, info) -> Optional[Any]:
    return data.get(field)


def strict_get(field: str, data, info) -> Any:
    return data[field]


def test_string_list():
    class Query(TypedGraphQLObject):
        def user(data, info) -> Iterable[str]:
            yield from iter(["abc", "def"])

    schema = GraphQLSchema(query=Query.graphql_type)
    result = graphql_sync(schema, "{user}")
    assert result.data == {"user": ["abc", "def"]}
    assert result.errors is None


def test_string_list_with_snake_cased_arg():
    class Query(TypedGraphQLObject):
        def user(data, info, phone_number: int = 0) -> Iterable[str]:
            yield from iter(["abc", "def"])

    schema = GraphQLSchema(query=Query.graphql_type)
    result = graphql_sync(schema, "{user(phoneNumber: 10)}")
    assert result.data == {"user": ["abc", "def"]}
    assert result.errors is None
