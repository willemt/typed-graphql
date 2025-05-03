from dataclasses import dataclass
from functools import wraps
from typing import Any, Generic, Iterable, List, Optional, Tuple, TypedDict, TypeVar

from graphql import graphql_sync
from graphql.type import GraphQLField, GraphQLSchema, GraphQLString, GraphQLObjectType

from typed_graphql import (
    TypedGraphqlMiddlewareManager,
    graphql_type,
    resolver,
    resolverclass,
    staticresolver,
)

from graphql import print_schema


def test_docstrings():
    @dataclass
    class User:
        """A user agent"""

        value: str

    class Query:
        def resolve_user(self, info, pk: str) -> List[User]:
            """
            :param pk: The primary key
            """
            return [User("1")]

    assert str(graphql_type(Query).fields["user"].type) == "[User!]!"
    schema = GraphQLSchema(query=graphql_type(Query))
    assert (
        print_schema(schema)
        == """type Query {
  user(
    \"\"\"The primary key\"\"\"
    pk: String!
  ): [User!]!
}

\"\"\"A user agent\"\"\"
type User {
  value: String!
}"""
    )


def test_docstring_with_resolver_decorator():
    @dataclass
    class User:
        value: str

    class Query:
        @resolver
        def user(self, info, pk: str) -> List[User]:
            """
            :param pk: The primary key
            """
            return [User("1")]

    assert str(graphql_type(Query).fields["user"].type) == "[User!]!"
    schema = GraphQLSchema(query=graphql_type(Query))
    assert (
        print_schema(schema)
        == """type Query {
  user(
    \"\"\"The primary key\"\"\"
    pk: String!
  ): [User!]!
}

\"\"\"User(value: str)\"\"\"
type User {
  value: String!
}"""
    )


def test_docstring_with_staticresolver_decorator():
    @dataclass
    class User:
        """A user agent"""

        value: str

    class Query:
        @staticresolver
        def user(data, info, pk: str) -> List[User]:
            """
            :param pk: The primary key
            """
            return [User("1")]

    assert str(graphql_type(Query).fields["user"].type) == "[User!]!"
    schema = GraphQLSchema(query=graphql_type(Query))
    assert (
        print_schema(schema)
        == """type Query {
  user(
    \"\"\"The primary key\"\"\"
    pk: String!
  ): [User!]!
}

\"\"\"A user agent\"\"\"
type User {
  value: String!
}"""
    )


def test_docstring_class():
    @dataclass
    class User:
        """
        A user agent
        """

        value: str

    class Query:
        """
        A query for pulling data
        """

        @staticresolver
        def user(data, info, pk: str) -> List[User]:
            """
            The user that we want to query
            :param pk: The primary key
            """
            return [User("1")]

    assert str(graphql_type(Query).fields["user"].type) == "[User!]!"
    schema = GraphQLSchema(query=graphql_type(Query))
    assert (
        print_schema(schema)
        == """\"\"\"A query for pulling data\"\"\"
type Query {
  user(
    \"\"\"The primary key\"\"\"
    pk: String!
  ): [User!]!
}

\"\"\"A user agent\"\"\"
type User {
  value: String!
}"""
    )


def test_docstring_with_dataclass_docstring():
    @dataclass
    class User:
        """
        A user agent
        :param value: The important value
        """

        value: str

    class Query:
        @staticresolver
        def user(data, info, pk: str) -> List[User]:
            return [User("1")]

    assert str(graphql_type(Query).fields["user"].type) == "[User!]!"
    schema = GraphQLSchema(query=graphql_type(Query))
    assert (
        print_schema(schema)
        == """type Query {
  user(pk: String!): [User!]!
}

\"\"\"A user agent\"\"\"
type User {
  \"\"\"The important value\"\"\"
  value: String!
}"""
    )
