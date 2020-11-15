from typing import Any, List, Optional

from graphql import graphql_sync
from graphql.type import GraphQLSchema

from typed_graphql import SimpleResolver, TypedGraphQLObject


def get(field: str, data, info) -> Optional[Any]:
    return data.get(field)


def strict_get(field: str, data, info) -> Any:
    return data[field]


def test_mutation():
    class User(TypedGraphQLObject):
        name: SimpleResolver[str] = lambda d, info: d["name"]

    class Query(TypedGraphQLObject):
        user: SimpleResolver[str] = lambda data, info: ""

    class Mutation(TypedGraphQLObject):
        def create_user(
            data,
            info,
            phone_number: str = "",
            groups: Optional[List[str]] = None,
            name: Optional[str] = None,
            size: float = None,
        ) -> User:
            return User({"name": name})


    schema = GraphQLSchema(query=Query.graphql_type, mutation=Mutation.graphql_type)
    result = graphql_sync(schema, """
    mutation createUser {
        createUser(size: 100, name: "XXX", phoneNumber: "10") {
            name
        }
    }
    """)
    assert result.data == {"createUser": {"name": "XXX"}}
