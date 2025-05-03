# from __future__ import annotations

from graphql import graphql_sync
from graphql.type import GraphQLSchema

from typed_graphql import (
    graphql_type,
    staticresolver,
)


def test_optional_str_py_3_10():
    class Query:
        @staticresolver
        def user(data, info, x: str | None = None) -> str:
            return "a string!"

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user}")
    assert result.data == {"user": "a string!"}
    assert result.errors is None
    assert str(graphql_type(Query).fields["user"].type) == "String!"


def test_string_list_py3_10():
    class Query:
        @staticresolver
        def user(data, info) -> list[str]:
            return ["abc", "def"]

    assert str(graphql_type(Query).fields["user"].type) == "[String!]!"

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user}")
    assert result.data == {"user": ["abc", "def"]}
    assert result.errors is None
