from dataclasses import dataclass
from datetime import date
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


def test_date_schema():
    @dataclass
    class User:
        login: date
        created: date

    class Query:
        def resolve_user(self, info) -> List[User]:
            return [
                User(
                    date(2020, 1, 1),
                    date(2019, 1, 1),
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

\"\"\"User(login: datetime.date, created: datetime.date)\"\"\"
type User {
  login: Date!
  created: Date!
}

scalar Date"""
    )


def test_date_uses_date_scalar():
    @dataclass
    class User:
        login: date
        created: date

    class Query:
        def resolve_user(self, info) -> List[User]:
            return [
                User(
                    date(2020, 1, 1),
                    date(2019, 1, 1),
                )
            ]

    assert str(graphql_type(Query).fields["user"].type) == "[User!]!"
    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(
        schema, "{user { login }}", Query(), middleware=TypedGraphqlMiddlewareManager()
    )
    assert result.data == {"user": [{"login": "2020-01-01"}]}
    assert result.errors is None


def test_date_must_be_date():
    @dataclass
    class User:
        login: date

    class Query:
        def resolve_user(self, info) -> List[User]:
            return [User("haha garbage")]  # type: ignore

    assert str(graphql_type(Query).fields["user"].type) == "[User!]!"
    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(
        schema, "{user { login }}", Query(), middleware=TypedGraphqlMiddlewareManager()
    )
    assert result.errors[0].message == "Value is not a date instance"


def test_date_optional():
    @dataclass
    class User:
        login: Optional[date]

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
