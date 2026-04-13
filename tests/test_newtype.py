from dataclasses import dataclass
from typing import NewType
from typing import Optional

from graphql import graphql_sync
from graphql.type import GraphQLSchema

from typed_graphql import TypedGraphqlMiddlewareManager
from typed_graphql import graphql_type
from typed_graphql import resolverclass
from typed_graphql import staticresolver

MyId = NewType("MyId", str)
WidgetId = NewType("WidgetId", str)


@resolverclass()
@dataclass
class Widget:
    id: WidgetId
    name: str


@resolverclass()
@dataclass
class WidgetForwardRef:
    # String annotations exercise the same resolution path as
    # `from __future__ import annotations` (PEP 563).
    id: "WidgetId"
    name: "str"


def test_newtype_can_be_nullable():
    class Query:
        @staticresolver
        def user(data, info, id: Optional[MyId] = None) -> str:
            return "xxx"

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user}")
    assert result.errors is None
    assert str(graphql_type(Query).fields["user"].args["id"].type) == "String"


def test_newtype_can_be_nullable_with_middleware():
    class Query:
        @staticresolver
        def get_user(data, info, id: MyId) -> str:
            return "xxx"

    schema = GraphQLSchema(query=graphql_type(Query))

    result = graphql_sync(
        schema, '{getUser(id: "1")}', middleware=TypedGraphqlMiddlewareManager()
    )
    assert result.errors is None
    assert result.data == {"getUser": "xxx"}


def test_newtype_on_dataclass_field():
    class Query:
        @staticresolver
        def widgets(data, info) -> list[Widget]:
            return [Widget(id=WidgetId("1"), name="first")]

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{widgets {id name}}")
    assert result.errors is None
    assert result.data == {"widgets": [{"id": "1", "name": "first"}]}


def test_newtype_on_dataclass_field_with_string_annotation():
    # Regression for NewType (and any type) failing when dataclass field
    # annotations are strings — e.g. under `from __future__ import annotations`.
    class Query:
        @staticresolver
        def widgets(data, info) -> list[WidgetForwardRef]:
            return [WidgetForwardRef(id=WidgetId("1"), name="first")]

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{widgets {id name}}")
    assert result.errors is None
    assert result.data == {"widgets": [{"id": "1", "name": "first"}]}
