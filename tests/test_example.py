from typing import Any
from typing import List
from typing import Optional

from graphql import graphql_sync
from graphql.type import GraphQLField
from graphql.type import GraphQLObjectType
from graphql.type import GraphQLSchema
from graphql.type import GraphQLString

from typed_graphql import graphql_type
from typed_graphql import staticresolver


def get(field: str, data, info) -> Optional[Any]:
    return data.get(field)


def strict_get(field: str, data, info) -> Any:
    return data[field]


class User(dict):
    # Regular method
    @staticresolver
    def name(data, info) -> str:
        return data.get("name", "") + "1"

    # Optional respects not null types
    # Auto camelCases the attribute
    @staticresolver
    def optional_name(data, info) -> Optional[str]:
        return data.get("name", "") + "1"

    # Method with typed argument
    @staticresolver
    def addresses(data, info, limit: int) -> List[str]:
        return ["address1", "address2"]

    @staticresolver
    def enabled(data, info) -> bool:
        return data["status"]


class Query:
    @staticresolver
    def users(data, info) -> List[User]:
        return [User({"name": "xxx", "status": False, "rate": 0.1})]


query = graphql_type(Query)
schema = GraphQLSchema(query=query)

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
    class Status(dict):
        @staticresolver
        def text(data, info) -> str:
            return "enabled"

    class User(dict):
        @staticresolver
        def value(data, info) -> str:
            return data["value"]

        @staticresolver
        def status(data, info) -> Status:
            return Status()

    query = GraphQLObjectType(
        "Query",
        lambda: {
            "user": GraphQLField(
                graphql_type(User), resolve=lambda d, i: User({"value": "xxx"})
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

    class User(dict):
        @staticresolver
        def value(d, info) -> str:
            return d["value"]

        # Can't do this because "Status" isn't a type
        # status: SimpleResolver[Status] = lambda d, info: {"something": "xxx"}

        @staticresolver
        def status(data, info) -> Status:
            return {"something": "enabled"}  # type: ignore

    query = GraphQLObjectType(
        "Query",
        lambda: {
            "user": GraphQLField(
                graphql_type(User), resolve=lambda d, i: User({"value": "xxx"})
            )
        },
    )

    schema = GraphQLSchema(query=query)
    result = graphql_sync(schema, "{user {value status { text }}}")
    assert result.data == {'user': {'status': {'text': 'enabled'}, 'value': 'xxx'}}
