from dataclasses import dataclass
from datetime import datetime
from typing import Any
from typing import Generic
from typing import List
from typing import Optional
from typing import TypeVar
from typing import cast

from graphql import graphql_sync
from graphql.type import GraphQLSchema

from typed_graphql import TypedGraphqlMiddlewareManager
from typed_graphql import graphql_type
from typed_graphql import resolver
from typed_graphql import resolverclass


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
    assert result.data == {"user": [{'value': '1', 'xxx': 'abc'}]}
    assert result.errors is None


def test_dataclass_with_decorator():
    @resolverclass()
    @dataclass
    class User:
        xxx: Optional[str] = None

    class Query:
        def resolve_user(self, info) -> List[User]:
            return [User("1")]

    assert str(graphql_type(Query).fields["user"].type) == '[User!]!'
    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user { xxx }}", Query(), middleware=TypedGraphqlMiddlewareManager())
    assert result.data == {"user": [{'xxx': '1'}]}


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


def test_dataclass_inheritance_passes_on_fields():
    @dataclass
    class Thing:
        value: str

    @dataclass
    class User(Thing):
        xxx: Optional[str] = None

    class Query:
        def resolve_user(self, info) -> List[User]:
            return [User("1")]

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user { value xxx }}", Query(), middleware=TypedGraphqlMiddlewareManager())
    assert result.data == {'user': [{'value': '1', 'xxx': None}]}


def test_dataclass_inheritance_passes_on_resolver_fields():
    @dataclass
    class Thing:
        @resolver
        def value(self, info) -> str:
            return "z"

    @dataclass
    class User(Thing):
        xxx: Optional[str] = None

    class Query:
        def resolve_user(self, info) -> List[User]:
            return [User("1")]

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user { value xxx }}", Query(), middleware=TypedGraphqlMiddlewareManager())
    assert result.data == {'user': [{'value': 'z', 'xxx': '1'}]}


def test_dataclass_inheritance_passes_on_resolver_fields_with_snake_case():
    @dataclass
    class Thing:
        @resolver
        def my_value(self, info) -> str:
            return "z"

    @dataclass
    class User(Thing):
        xxx: Optional[str] = None

    class Query:
        def resolve_user(self, info) -> List[User]:
            return [User("1")]

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user { myValue xxx }}", Query(), middleware=TypedGraphqlMiddlewareManager())
    assert result.data == {'user': [{'myValue': 'z', 'xxx': '1'}]}


def test_generic():
    X = TypeVar('X')

    @dataclass
    class Paged(Generic[X]):
        @resolver
        def my_value(self, info) -> X:
            return cast(X, "z")

    @dataclass
    class User(Paged[str]):
        xxx: Optional[str] = None

    class Query:
        def resolve_user(self, info) -> List[User]:
            return [User("1")]

    assert str(graphql_type(User).fields["myValue"].type) == 'String!'
    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user { myValue xxx }}", Query(), middleware=TypedGraphqlMiddlewareManager())
    assert result.data == {'user': [{'myValue': 'z', 'xxx': '1'}]}


def test_optional_generic():
    X = TypeVar('X')

    @dataclass
    class Paged(Generic[X]):
        @resolver
        def my_value(self, info) -> Optional[X]:
            return "z"

    @dataclass
    class User(Paged[str]):
        xxx: Optional[str] = None

    class Query:
        def resolve_user(self, info) -> List[User]:
            return [User("1")]

    assert str(graphql_type(User).fields["myValue"].type) == 'String'
    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user { myValue xxx }}", Query(), middleware=TypedGraphqlMiddlewareManager())
    assert result.data == {'user': [{'myValue': 'z', 'xxx': '1'}]}


def test_dataclass_prefers_resolvers_first():
    @dataclass
    class User:
        value: datetime

        def resolve_value(self, info) -> str:
            return "xxx"

    class Query:
        def resolve_user(self, info) -> List[User]:
            return [User("1")]

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user { value }}", Query(), middleware=TypedGraphqlMiddlewareManager())
    assert result.data == {'user': [{'value': 'xxx'}]}
