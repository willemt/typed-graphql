from typing import NewType
from typing import Optional

from graphql import graphql_sync
from graphql.type import GraphQLSchema

from typed_graphql import TypedGraphqlMiddlewareManager
from typed_graphql import graphql_type
from typed_graphql import staticresolver


MyId = NewType("MyId", str)


def test_newtype_can_be_nullable():
    class Query:
        @staticresolver
        def user(data, info, id: Optional[MyId] = None) -> str:
            return "xxx"

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user}")
    assert result.errors is None
    assert str(graphql_type(Query).fields["user"].args["id"].type) == "String"


def test_newtype_can_be_nullable_with_middleware():
    class Query:
        @staticresolver
        def get_user(data, info, id: MyId) -> str:
            return "xxx"

    schema = GraphQLSchema(query=graphql_type(Query))

    result = graphql_sync(
        schema, '{getUser(id: "1")}', middleware=TypedGraphqlMiddlewareManager()
    )
    assert result.errors is None
    assert result.data == {"getUser": "xxx"}
