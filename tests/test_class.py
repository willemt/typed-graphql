from dataclasses import dataclass
from functools import wraps
from typing import Any, Generic, Iterable, List, Optional, Tuple, TypedDict, TypeVar

from graphql import graphql_sync
from graphql.type import GraphQLField, GraphQLSchema, GraphQLString, GraphQLObjectType

from typed_graphql import TypedGraphqlMiddlewareManager, graphql_type, resolver, resolverclass, staticresolver


def test_class():
    class User:
        def __init__(self, data):
            self.data = data

        def resolve_value(self, info) -> str:
            return self.data

    class Query:
        def resolve_user(self, info) -> List[User]:
            return [User("1")]

    assert str(graphql_type(Query).fields["user"].type) == '[User!]!'
    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user { value }}", Query(), middleware=TypedGraphqlMiddlewareManager())
    assert result.data == {"user": [{"value": "1"}]}
    assert result.errors is None


def test_snake_case():
    class User:
        def __init__(self, data):
            self.data = data

        def resolve_my_value(self, info) -> str:
            return self.data

    class Query:
        def resolve_user(self, info) -> List[User]:
            return [User("1")]

    assert str(graphql_type(Query).fields["user"].type) == '[User!]!'
    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user { myValue }}", Query(), middleware=TypedGraphqlMiddlewareManager())
    print(result.errors)
    assert result.data == {"user": [{"myValue": "1"}]}
    assert result.errors is None
