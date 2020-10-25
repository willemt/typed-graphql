from functools import partial
from typing import Any, List, Optional

from graphql import graphql_sync
from graphql.type import GraphQLField, GraphQLObjectType, GraphQLSchema, GraphQLString

from typed_graphql import SimpleResolver, TypedGraphQLObject


def get(field: str, data, info) -> Optional[Any]:
    return data.get(field)


def strict_get(field: str, data, info) -> Any:
    return data[field]


class User(TypedGraphQLObject):

    # Regular method
    def name(data, info) -> str:
        return data.get("name") + "1"

    # Optional respects not null types
    # Auto camelCases the attribute
    def optional_name(data, info) -> Optional[str]:
        return data.get("name") + "1"

    # Method with typed argument
    def addresses(data, info, limit: int) -> List[str]:
        return ["address1", "address2"]

    # Function assignment
    enabled: SimpleResolver[bool] = partial(strict_get, "status")


class Query(TypedGraphQLObject):
    def users(data, info) -> List[User]:
        return [User({"name": "xxx", "status": False, "rate": 0.1})]


query = Query.graphql_type
schema = GraphQLSchema(query=Query.graphql_type)

QUERY = """
{
    users {
        enabled
        name
        optionalName
        addresses(limit: 1)
    }
}
"""


def test_example():
    result = graphql_sync(schema, QUERY)
    assert result.data == {
        "users": [
            {
                "enabled": False,
                "name": "xxx1",
                "optionalName": "xxx1",
                "addresses": ["address1", "address2"],
            }
        ]
    }
    assert result.errors is None


def test_interpersed_usage():
    class Status(TypedGraphQLObject):
        text: SimpleResolver[str] = lambda data, info: "enabled"

    class User(TypedGraphQLObject):
        value: SimpleResolver[str] = lambda data, info: data["value"]
        status: SimpleResolver[Status] = lambda data, info: Status()

    query = GraphQLObjectType(
        "Query",
        lambda: {
            "user": GraphQLField(
                User.graphql_type, resolve=lambda d, i: User({"value": "xxx"})
            )
        },
    )

    schema = GraphQLSchema(query=query)
    result = graphql_sync(schema, "{user {value status {text}}}")
    assert result.data == {'user': {'status': {'text': 'enabled'}, 'value': 'xxx'}}


def test_interpersed_usage_with_sub_selections():
    Status = GraphQLObjectType( # NOQA
        "Status",
        {
            "text": GraphQLField(GraphQLString, resolve=lambda data, info: data["something"])
        })

    class User(TypedGraphQLObject):
        value: SimpleResolver[str] = lambda d, info: d["value"]

        # Can't do this because "Status" isn't a type
        # status: SimpleResolver[Status] = lambda d, info: {"something": "xxx"}

        def status(data, info) -> Status:
            return {"something": "xxx"}  # type: ignore

    query = GraphQLObjectType(
        "Query",
        lambda: {
            "user": GraphQLField(
                User.graphql_type, resolve=lambda d, i: User({"value": "xxx"})
            )
        },
    )

    schema = GraphQLSchema(query=query)
    result = graphql_sync(schema, "{user {value}}")
    assert result.data == {"user": {"value": "xxx"}}
