from dataclasses import dataclass
from typing import List
from typing import Optional
from typing import TypedDict

from graphql import graphql_sync
from graphql.type import GraphQLSchema

from typed_graphql import TypedGraphqlMiddlewareManager
from typed_graphql import graphql_type
from typed_graphql import staticresolver


class Animal(TypedDict):
    name: str


def test_typeddict():
    @dataclass
    class User:
        value: Animal

    class Query:
        def resolve_user(self, info) -> List[User]:
            return [User(Animal({"name": "cat"}))]

    assert str(graphql_type(Query).fields["user"].type) == "[User!]!"
    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(
        schema,
        "{user { value { name} }}",
        Query(),
        middleware=TypedGraphqlMiddlewareManager(),
    )
    print(result)
    assert result.data["user"][0]["value"]["name"] == "cat"
    assert result.errors is None


class Category(TypedDict):
    animal: Optional[Animal]
    name: str


def test_typeddict_input():
    # class AnimalInput(TypedDict):
    #     name: str

    class User(dict):
        @staticresolver
        def name(d, info) -> str:
            return d["name"]

        @staticresolver
        def category(d, info) -> Category:
            pass

    class Query:
        @staticresolver
        def user(data, info) -> str:
            return ""

    class Mutation:
        @staticresolver
        def create_user(
            data,
            info,
            category: Category,
        ) -> User:
            return User({"name": "xxx"})

    schema = GraphQLSchema(query=graphql_type(Query), mutation=graphql_type(Mutation))
    result = graphql_sync(
        schema,
        """
    mutation createUser {
        createUser(category: {animal: {name: "test"}, name: "10"}) {
            name
        }
    }
    """,
    )
    print(result)
    assert result.data == {"createUser": {"name": "xxx"}}
