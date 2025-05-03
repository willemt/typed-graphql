from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from typing import Any
from typing import List
from typing import Optional

from graphql import graphql_sync
from graphql.type import GraphQLSchema
from graphql.utilities import print_schema

from typed_graphql import TypedGraphqlMiddlewareManager
from typed_graphql import graphql_type


def get(field: str, data, info) -> Optional[Any]:
    return data.get(field)


def strict_get(field: str, data, info) -> Any:
    return data[field]


def test_datetime_schema():
    @dataclass
    class User:
        login: datetime
        created: datetime

    class Query:
        def resolve_user(self, info) -> List[User]:
            return [
                User(
                    datetime(2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                    datetime(2019, 1, 1, 1, 1, 1, tzinfo=timezone.utc),
                )
            ]

    assert (
        print_schema(
            GraphQLSchema(
                query=graphql_type(Query),
            )
        )
        == """type Query {
  user: [User!]!
}

\"\"\"User(login: datetime.datetime, created: datetime.datetime)\"\"\"
type User {
  login: DateTime!
  created: DateTime!
}

scalar DateTime"""
    )


def test_datetime_uses_datetime_scalar():
    @dataclass
    class User:
        login: datetime
        created: datetime

    class Query:
        def resolve_user(self, info) -> List[User]:
            return [
                User(
                    datetime(2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                    datetime(2019, 1, 1, 1, 1, 1, tzinfo=timezone.utc),
                )
            ]

    assert str(graphql_type(Query).fields["user"].type) == "[User!]!"
    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(
        schema, "{user { login }}", Query(), middleware=TypedGraphqlMiddlewareManager()
    )
    assert result.data == {"user": [{"login": "2020-01-01T00:00:00.000000Z"}]}
    assert result.errors is None


def test_datetime_must_be_utc():
    @dataclass
    class User:
        login: datetime

    class Query:
        def resolve_user(self, info) -> List[User]:
            return [
                User(
                    datetime(2020, 1, 1, 0, 0, 0, tzinfo=None),
                )
            ]

    assert str(graphql_type(Query).fields["user"].type) == "[User!]!"
    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(
        schema, "{user { login }}", Query(), middleware=TypedGraphqlMiddlewareManager()
    )
    assert result.errors[0].message == "Datetime must UTC"


def test_datetime_must_be_datetime():
    @dataclass
    class User:
        login: datetime

    class Query:
        def resolve_user(self, info) -> List[User]:
            return [User("haha garbage")]  # type: ignore

    assert str(graphql_type(Query).fields["user"].type) == "[User!]!"
    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(
        schema, "{user { login }}", Query(), middleware=TypedGraphqlMiddlewareManager()
    )
    assert result.errors[0].message == "Value is not a datetime instance"


def test_datetime_optional():
    @dataclass
    class User:
        login: Optional[datetime]

    class Query:
        def resolve_user(self, info) -> List[User]:
            return [User(None)]

    assert str(graphql_type(Query).fields["user"].type) == "[User!]!"
    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(
        schema, "{user { login }}", Query(), middleware=TypedGraphqlMiddlewareManager()
    )
    assert result.data == {"user": [{"login": None}]}
    assert result.errors is None
