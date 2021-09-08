from functools import wraps
from typing import Any, Iterable, List, Optional, Tuple

from graphql import graphql_sync
from graphql.type import GraphQLField, GraphQLSchema, GraphQLString, GraphQLObjectType

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
    assert str(Query.graphql_type.fields["user"].type) == 'Int!'


def test_bool():
    class Query(TypedGraphQLObject):
        def user(data, info) -> bool:
            return True

    schema = GraphQLSchema(query=Query.graphql_type)
    result = graphql_sync(schema, "{user}")
    assert result.data == {"user": True}
    assert result.errors is None
    assert str(Query.graphql_type.fields["user"].type) == 'Boolean!'


def test_expects_int():
    class Query(TypedGraphQLObject):
        def user(data, info) -> int:
            return "xxx"  # type: ignore

    schema = GraphQLSchema(query=Query.graphql_type)
    result = graphql_sync(schema, "{user}")
    assert result.data is None
    assert str(result.errors[0]).startswith("Int cannot represent non-integer value: 'xxx'")


def test_str():
    class Query(TypedGraphQLObject):
        def user(data, info) -> str:
            return "a string!"

    schema = GraphQLSchema(query=Query.graphql_type)
    result = graphql_sync(schema, "{user}")
    assert result.data == {"user": "a string!"}
    assert result.errors is None
    assert str(Query.graphql_type.fields["user"].type) == 'String!'


def test_optional_str():
    class Query(TypedGraphQLObject):
        def user(data, info, x: Optional[str] = None) -> str:
            return "a string!"

    schema = GraphQLSchema(query=Query.graphql_type)
    result = graphql_sync(schema, "{user}")
    assert result.data == {"user": "a string!"}
    assert result.errors is None
    assert str(Query.graphql_type.fields["user"].type) == 'String!'


def test_string_list():
    class Query(TypedGraphQLObject):
        def user(data, info) -> List[str]:
            return ["abc", "def"]

    assert str(Query.graphql_type.fields["user"].type) == '[String!]'

    schema = GraphQLSchema(query=Query.graphql_type)
    result = graphql_sync(schema, "{user}")
    assert result.data == {"user": ["abc", "def"]}
    assert result.errors is None


def test_string_tuple():
    class Query(TypedGraphQLObject):
        def user(data, info) -> Tuple[str, str]:
            return "abc", "def"

    assert str(Query.graphql_type.fields["user"].type) == '[String!]'

    schema = GraphQLSchema(query=Query.graphql_type)
    result = graphql_sync(schema, "{user}")
    assert result.data == {"user": ["abc", "def"]}
    assert result.errors is None


def test_iterable():
    class Query(TypedGraphQLObject):
        def user(data, info) -> Iterable[str]:
            return ["abc", "def"]

    assert str(Query.graphql_type.fields["user"].type) == '[String!]'


def test_graphql_object_type():
    Status = GraphQLObjectType( # NOQA
        "Status",
        {
            "text": GraphQLField(GraphQLString, resolve=lambda data, info: data["something"])
        })

    class Query(TypedGraphQLObject):
        def user(data, info) -> Status:
            return {"something": "sometext"}

    assert str(Query.graphql_type.fields["user"].type) == 'Status!'

    schema = GraphQLSchema(query=Query.graphql_type)
    result = graphql_sync(schema, "{user { text } }")
    assert result.data == {"user": {"text": "sometext"}}
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


def test_auto_camelcase_attribute():
    class User(TypedGraphQLObject):
        my_value: SimpleResolver[str] = lambda d, info: d["value"]

    class Query(TypedGraphQLObject):
        user: SimpleResolver[User] = lambda data, info: User({"value": "xxx"})

    schema = GraphQLSchema(query=Query.graphql_type)
    result = graphql_sync(schema, "{user {myValue}}")
    assert result.data == {"user": {"myValue": "xxx"}}


def test_auto_camelcase_argument():
    class User(TypedGraphQLObject):
        def value(data, info, phone_number: str = "") -> str:
            return "zzz"

    class Query(TypedGraphQLObject):
        user: SimpleResolver[User] = lambda data, info: User({"value": "xxx"})

    schema = GraphQLSchema(query=Query.graphql_type)
    result = graphql_sync(schema, '{user {value(phoneNumber: "100")}}')
    assert result.data == {"user": {"value": "zzz"}}


def my_wrapper(func):
    @wraps(func)
    def wrapper(data, info, **kwargs):
        return func(data, info, **kwargs)
    return wrapper


def test_decorated_attribute_works_fine():
    class User(TypedGraphQLObject):
        @my_wrapper
        def value(data, info, phonenumber: str = "") -> str:
            return "zzz"

    class Query(TypedGraphQLObject):
        user: SimpleResolver[User] = lambda data, info: User({"value": "xxx"})

    schema = GraphQLSchema(query=Query.graphql_type)
    result = graphql_sync(schema, '{user {value(phonenumber: "100")}}')
    assert result.data == {"user": {"value": "zzz"}}


def test_osupports_default_argument_on_get_method():
    class User(TypedGraphQLObject):
        def value(data, info, phonenumber: str = "") -> str:
            return data.get("valuex", "xxx")

    class Query(TypedGraphQLObject):
        user: SimpleResolver[User] = lambda data, info: User({"value": "123"})

    schema = GraphQLSchema(query=Query.graphql_type)
    result = graphql_sync(schema, '{user {value(phonenumber: "100")}}')
    assert result.data == {"user": {"value": "xxx"}}


def test_simple_resolver_uses_function():
    def resolve_user(data, info):
        return {"value": "xxx"}

    class User(TypedGraphQLObject):
        def value(data, info, phonenumber: str = "") -> str:
            return "zzz"

    class Query(TypedGraphQLObject):
        user: SimpleResolver[User] = resolve_user

    schema = GraphQLSchema(query=Query.graphql_type)
    result = graphql_sync(schema, '{user {value(phonenumber: "100")}}')
    assert result.data == {"user": {"value": "zzz"}}


def test_assigned_function_works_fine():
    def resolve_value(data, info, phonenumber: str) -> str:
        return "100"

    class User(TypedGraphQLObject):
        value = resolve_value

    def resolve_user(data, info) -> User:
        return User({"value": "xxx"})

    class Query(TypedGraphQLObject):
        user = resolve_user

    schema = GraphQLSchema(query=Query.graphql_type)
    result = graphql_sync(schema, '{user {value(phonenumber: "100")}}')
    assert result.data == {"user": {"value": "100"}}


def test_object_type_can_be_referenced_more_than_once():
    class User(TypedGraphQLObject):
        def value(data, info) -> str:
            return "xxx"

    class Query(TypedGraphQLObject):
        def users(data, info) -> Iterable[User]:
            return [User({})]

        def users2(data, info) -> Iterable[User]:
            return [User({})]

    schema = GraphQLSchema(query=Query.graphql_type)
    result = graphql_sync(schema, '{users {value}}')
    assert result.data == {'users': [{'value': 'xxx'}]}
