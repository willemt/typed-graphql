from dataclasses import dataclass
from functools import wraps
from typing import Any, Iterable, List, NewType, Optional, Tuple, TypedDict

from graphql import graphql_sync
from graphql.type import GraphQLField, GraphQLSchema, GraphQLString, GraphQLObjectType

from typed_graphql import (
    ReturnTypeMissing,
    TypedGraphqlMiddlewareManager,
    graphql_type,
    resolver,
    staticresolver,
)


MyId = NewType("MyId", str)


def test_newtype_can_be_nullable():

    class Query:
        @staticresolver
        def user(data, info, id: Optional[MyId] = None) -> str:
            return "xxx"

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user}")
    # assert result.data == {"user": "xxx"}
    # assert result.errors is None
    assert str(graphql_type(Query).fields["user"].args["id"].type ) == 'String'
