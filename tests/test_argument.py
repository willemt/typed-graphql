from typing import Optional

from graphql.utilities import print_schema
from graphql.type import GraphQLSchema

from typed_graphql import graphql_type
from typed_graphql import staticresolver


def test_mutation_input_default():
    class User(dict):
        @staticresolver
        def name(d, info) -> str:
            return d["name"]

    class Query:
        @staticresolver
        def user(data, info) -> str:
            return ""

    class Mutation:
        @staticresolver
        def create_user(
            data,
            info,
            test: Optional[str],
            phone_number: Optional[str] = "000",
        ) -> User:
            return User({"name": "abc"})

    assert print_schema(GraphQLSchema(query=graphql_type(Query), mutation=graphql_type(Mutation))) == """type Query {
  user: String!
}

type Mutation {
  createUser(test: String, phoneNumber: String = "000"): User!
}

type User {
  name: String!
}"""


def test_query_input_default():
    class Query:
        @staticresolver
        def user(data, info, phone_number: Optional[str] = "000") -> str:
            return ""

    assert print_schema(GraphQLSchema(query=graphql_type(Query))) == """type Query {
  user(phoneNumber: String = "000"): String!
}"""
