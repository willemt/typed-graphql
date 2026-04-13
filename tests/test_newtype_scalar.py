"""Tests that NewType produces named custom scalars in the GraphQL schema."""
from typing import NewType, Optional

import pytest
from graphql import build_ast_schema, graphql_sync, print_schema
from graphql.type import GraphQLScalarType, GraphQLSchema

from typed_graphql import graphql_type, staticresolver


# --- type definitions used across tests ---

UserId = NewType("UserId", str)
Score = NewType("Score", int)
Ratio = NewType("Ratio", float)
Flag = NewType("Flag", bool)


def test_newtype_str_becomes_named_scalar():
    class Query:
        @staticresolver
        def user_id(data, info) -> UserId:
            return UserId("abc-123")

    t = graphql_type(Query)
    field_type = t.fields["userId"].type
    # NonNull wrapping a named scalar
    assert str(field_type) == "UserId!"
    assert isinstance(field_type.of_type, GraphQLScalarType)
    assert field_type.of_type.name == "UserId"


def test_newtype_int_becomes_named_scalar():
    class Query:
        @staticresolver
        def score(data, info) -> Score:
            return Score(42)

    t = graphql_type(Query)
    field_type = t.fields["score"].type
    assert str(field_type) == "Score!"
    assert field_type.of_type.name == "Score"


def test_newtype_float_becomes_named_scalar():
    class Query:
        @staticresolver
        def ratio(data, info) -> Ratio:
            return Ratio(0.5)

    t = graphql_type(Query)
    field_type = t.fields["ratio"].type
    assert str(field_type) == "Ratio!"
    assert field_type.of_type.name == "Ratio"


def test_newtype_bool_becomes_named_scalar():
    class Query:
        @staticresolver
        def flag(data, info) -> Flag:
            return Flag(True)

    t = graphql_type(Query)
    field_type = t.fields["flag"].type
    assert str(field_type) == "Flag!"
    assert field_type.of_type.name == "Flag"


def test_optional_newtype_is_nullable():
    class Query:
        @staticresolver
        def user_id(data, info) -> Optional[UserId]:
            return None

    t = graphql_type(Query)
    field_type = t.fields["userId"].type
    assert str(field_type) == "UserId"
    assert isinstance(field_type, GraphQLScalarType)
    assert field_type.name == "UserId"


def test_custom_scalar_via_graphql_type_hook():
    """A NewType with a manually attached _graphql_type gets that scalar in the schema."""
    EmailAddress = NewType("EmailAddress", str)
    EmailAddress._graphql_type = GraphQLScalarType(
        name="EmailAddress",
        serialize=lambda v: str(v).lower(),
        parse_value=lambda v: v,
    )

    class Query:
        @staticresolver
        def email(data, info) -> EmailAddress:
            return EmailAddress("User@Example.com")

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{ email }")
    assert result.errors is None
    # The custom serialize lowercases the value
    assert result.data == {"email": "user@example.com"}

    t = graphql_type(Query)
    field_type = t.fields["email"].type
    assert str(field_type) == "EmailAddress!"
    assert field_type.of_type.name == "EmailAddress"


def test_schema_sdl_shows_custom_scalars():
    """The printed SDL should declare UserId and Score as scalar types."""

    class Query:
        @staticresolver
        def user_id(data, info) -> UserId:
            return UserId("x")

        @staticresolver
        def score(data, info) -> Score:
            return Score(1)

    schema = GraphQLSchema(query=graphql_type(Query))
    sdl = print_schema(schema)
    assert "scalar UserId" in sdl
    assert "scalar Score" in sdl
