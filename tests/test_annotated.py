import asyncio
from typing import Annotated, Any, Optional

from graphql import GraphQLScalarType, GraphQLError, graphql
from graphql.type import GraphQLSchema

from typed_graphql import TypedGraphqlMiddlewareManager, TypeUnrepresentableAsGraphql, graphql_type


def get(field: str, data, info) -> Optional[Any]:
    return data.get(field)


def strict_get(field: str, data, info) -> Any:
    return data[field]


class NonEmptyString(GraphQLScalarType):
    """
    A custom scalar type for non-empty strings.
    """

    def __init__(self):
        super().__init__("NonEmptyString")

    @staticmethod
    def serialize(value):
        if not isinstance(value, str):
            raise GraphQLError(f"NonEmptyString cannot represent non-string value: {repr(value)}")
        if len(value.strip()) == 0:
            raise GraphQLError("NonEmptyString cannot represent empty string value.")
        return value

    @staticmethod
    def parse_value(value):
        if not isinstance(value, str):
            raise GraphQLError(f"NonEmptyString cannot represent non-string value: {repr(value)}")
        if len(value.strip()) == 0:
            raise GraphQLError("NonEmptyString cannot represent empty string value.")
        return value

    @staticmethod
    def parse_literal(node):
        if len(node.value.strip()) == 0:
            raise GraphQLError("NonEmptyString cannot represent empty string value.")
        return node.value


def test_annotated_type_overrides():
    class Query:
        def resolve_my_user(self, info) -> Annotated[str, NonEmptyString]:
            return "abc"

    schema = GraphQLSchema(query=graphql_type(Query))
    result = asyncio.new_event_loop().run_until_complete(
        graphql(schema, "{myUser}", Query(), middleware=TypedGraphqlMiddlewareManager())
    )
    assert result.errors is None
    assert result.data == {"myUser": "abc"}


def test_annotated_type_uses_validation():
    class Query:
        def resolve_my_user(self, info) -> Annotated[str, NonEmptyString]:
            return ""

    schema = GraphQLSchema(query=graphql_type(Query))
    result = asyncio.new_event_loop().run_until_complete(
        graphql(schema, "{myUser}", Query(), middleware=TypedGraphqlMiddlewareManager())
    )
    assert result.errors[0].message == "NonEmptyString cannot represent empty string value."
    assert result.data == {"myUser": None}


def test_annotated_type_uses_validation_without_middleware():
    class Query:
        def resolve_my_user(self, info) -> Annotated[str, NonEmptyString]:
            return ""

    schema = GraphQLSchema(query=graphql_type(Query))
    result = asyncio.new_event_loop().run_until_complete(
        graphql(schema, "{myUser}", Query())
    )
    # FIXME: there should be errors here?
    assert result.errors is None
    assert result.data == {"myUser": None}


def test_map_return_type_is_invalid():
    class Query:
        def resolve_my_user(self, info) -> map:
            return ""

    schema = GraphQLSchema(query=graphql_type(Query))
    result = asyncio.new_event_loop().run_until_complete(
        graphql(schema, "{myUser}", Query())
    )
    # FIXME: there should be errors here?
    assert result.errors[0].message == "Type map must define one or more fields."
