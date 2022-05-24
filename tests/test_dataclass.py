from dataclasses import dataclass
from functools import wraps
from typing import Any, Iterable, List, Optional, Tuple, TypedDict

from graphql import graphql_sync
from graphql.type import GraphQLField, GraphQLSchema, GraphQLString, GraphQLObjectType

from typed_graphql import TypedGraphqlMiddlewareManager, graphql_type, resolver, resolverclass, staticresolver


def get(field: str, data, info) -> Optional[Any]:
    return data.get(field)


def strict_get(field: str, data, info) -> Any:
    return data[field]


def test_dataclass_has_auto_resolvers():
    @dataclass
    class User:
        value: str

    class Query:
        def resolve_user(self, info) -> List[User]:
            return [User("1")]

    assert str(graphql_type(Query).fields["user"].type) == '[User!]!'
    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user { value }}", Query(), middleware=TypedGraphqlMiddlewareManager())
    print(result.errors)
    assert result.data == {"user": [{"value": "1"}]}
    assert result.errors is None


def test_dataclass_has_auto_resolvers_with_snake_casing():
    @dataclass
    class User:
        my_value: str

    class Query:
        def resolve_user(self, info) -> List[User]:
            return [User("1")]

    assert str(graphql_type(Query).fields["user"].type) == '[User!]!'
    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user { myValue }}", Query(), middleware=TypedGraphqlMiddlewareManager())
    print(result.errors)
    assert result.data == {"user": [{"myValue": "1"}]}
    assert result.errors is None


def test_dataclass_with_multiple_fields():
    @dataclass
    class User:
        xxx: str
        value: str

    class Query:
        def resolve_user(self, info) -> List[User]:
            return [User("abc", "1")]

    assert str(graphql_type(Query).fields["user"].type) == '[User!]!'
    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user { xxx value }}", Query(), middleware=TypedGraphqlMiddlewareManager())
    print(result.errors)
    assert result.data == {"user": [{'value': '1', 'xxx': 'abc'}]}
    assert result.errors is None


def test_dataclass_can_block_resolvers():

    @resolverclass(resolver_blocklist=["xxx"])
    @dataclass
    class User:
        value: str
        xxx: Optional[str] = None

    class Query:
        def resolve_user(self, info) -> List[User]:
            return [User("1")]

    assert str(graphql_type(Query).fields["user"].type) == '[User!]!'
    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user { xxx }}", Query(), middleware=TypedGraphqlMiddlewareManager())
    assert result.data is None
    assert result.errors[0].message == "Cannot query field 'xxx' on type 'User'."
