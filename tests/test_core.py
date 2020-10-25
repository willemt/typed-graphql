from functools import partial
from typing import Any, List, Optional

from graphql import graphql_sync
from graphql.type import GraphQLSchema

from typed_graphql import SimpleResolver, TypedGraphQLObject


def get(field: str, data, info) -> Optional[Any]:
    return data.get(field)


def strict_get(field: str, data, info) -> Any:
    return data[field]


def test_core():
    class Query(TypedGraphQLObject):
        def user(data, info) -> str:
            return "xxx"

    schema = GraphQLSchema(query=Query.graphql_type)
    result = graphql_sync(schema, "{user}")
    assert result.data == {"user": "xxx"}
    assert result.errors is None


def test_int():
    class Query(TypedGraphQLObject):
        def user(data, info) -> int:
            return 10

    schema = GraphQLSchema(query=Query.graphql_type)
    result = graphql_sync(schema, "{user}")
    assert result.data == {"user": 10}
    assert result.errors is None


def test_expects_int():
    class Query(TypedGraphQLObject):
        def user(data, info) -> int:
            return "xxx"

    schema = GraphQLSchema(query=Query.graphql_type)
    result = graphql_sync(schema, "{user}")
    assert result.data is None
    assert str(result.errors[0]).startswith("Int cannot represent non-integer value: 'xxx'")


def test_string_list():
    class Query(TypedGraphQLObject):
        def user(data, info) -> List[str]:
            return ["abc", "def"]

    schema = GraphQLSchema(query=Query.graphql_type)
    result = graphql_sync(schema, "{user}")
    assert result.data == {"user": ["abc", "def"]}
    assert result.errors is None


def test_function_assignment():
    class Query(TypedGraphQLObject):
        user: SimpleResolver[int] = lambda data, info: 55

    schema = GraphQLSchema(query=Query.graphql_type)
    result = graphql_sync(schema, "{user}")
    assert result.data == {"user": 55}
    assert result.errors is None


def test_argument():
    class Query(TypedGraphQLObject):
        def user(data, info, add: int) -> int:
            return 1 + add

    schema = GraphQLSchema(query=Query.graphql_type)
    result = graphql_sync(schema, "{user(add: 10)}")
    assert result.data == {"user": 11}
    assert result.errors is None


def test_optional_argument():
    class Query(TypedGraphQLObject):
        def user(data, info, add: Optional[int] = None) -> int:
            return 1

    schema = GraphQLSchema(query=Query.graphql_type)
    result = graphql_sync(schema, "{user}")
    assert result.data == {"user": 1}
    assert result.errors is None


def test_optional_argument_needs_default():
    class Query(TypedGraphQLObject):
        def user(data, info, add: Optional[int]) -> int:
            return 1

    schema = GraphQLSchema(query=Query.graphql_type)
    result = graphql_sync(schema, "{user}")
    assert result.data is None
    assert str(result.errors[0]).startswith("user() missing 1 required positional argument: 'add'")


def test_function_assignment_with_any():
    def return_11(data, info) -> Any:
        return 11

    class Query(TypedGraphQLObject):
        user: SimpleResolver[int] = return_11

    schema = GraphQLSchema(query=Query.graphql_type)
    result = graphql_sync(schema, "{user}")
    assert result.data == {"user": 11}


def test_function_assignment_with_annotated_class():
    class Query(TypedGraphQLObject):
        def name(data, info) -> str:
            return "aaa"

        enabled: SimpleResolver[bool] = lambda data, info: True

    schema = GraphQLSchema(query=Query.graphql_type)
    result = graphql_sync(schema, "{name}")
    assert result.data == {"name": "aaa"}


def test_mutation():
    class Query(TypedGraphQLObject):
        enabled: SimpleResolver[bool] = lambda data, info: True

    class Mutation(TypedGraphQLObject):
        save: SimpleResolver[bool] = lambda data, info: True

    schema = GraphQLSchema(query=Query.graphql_type, mutation=Mutation.graphql_type)
    result = graphql_sync(schema, "mutation {save}")
    assert result.data == {"save": True}


def test_sub_selection():
    class User(TypedGraphQLObject):
        value: SimpleResolver[str] = lambda d, info: d["value"]

    class Query(TypedGraphQLObject):
        user: SimpleResolver[User] = lambda data, info: User({"value": "xxx"})

    schema = GraphQLSchema(query=Query.graphql_type)
    result = graphql_sync(schema, "{user {value}}")
    assert result.data == {"user": {"value": "xxx"}}
