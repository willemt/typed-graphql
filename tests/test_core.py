from dataclasses import dataclass
from decimal import Decimal
from functools import wraps
from typing import Any
from typing import Iterable
from typing import List
from typing import Optional
from typing import TypedDict

from graphql import graphql_sync
from graphql.type import GraphQLField
from graphql.type import GraphQLObjectType
from graphql.type import GraphQLSchema
from graphql.type import GraphQLString

from typed_graphql import ReturnTypeMissing
from typed_graphql import TypedGraphqlMiddlewareManager
from typed_graphql import graphql_type
from typed_graphql import resolver
from typed_graphql import staticresolver


def get(field: str, data, info) -> Optional[Any]:
    return data.get(field)


def strict_get(field: str, data, info) -> Any:
    return data[field]


def test_core():
    class Query:
        @staticresolver
        def user(data, info) -> str:
            return "xxx"

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user}")
    assert result.data == {"user": "xxx"}
    assert result.errors is None
    assert str(graphql_type(Query).fields["user"].type) == "String!"


def test_resolve_prefix():
    class Query:
        @staticmethod
        def resolve_user(data, info) -> str:
            return "xxx"

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user}")
    assert result.data == {"user": "xxx"}
    assert result.errors is None


def test_resolve_prefix_with_object():
    class Query:
        def resolve_user(self, info) -> str:
            return "xxx"

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(
        schema, "{user}", Query(), middleware=TypedGraphqlMiddlewareManager()
    )
    assert result.data == {"user": "xxx"}
    assert result.errors is None


def test_resolve_prefix_with_object_with_data():
    class Query(dict):
        def resolve_user(self, info) -> str:
            return self.get("x", "")

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(
        schema, "{user}", Query(x=1), middleware=TypedGraphqlMiddlewareManager()
    )
    assert result.data == {"user": "1"}
    assert result.errors is None


def test_resolve_with_snake_case_argument():
    class Query(dict):
        def resolve_user(self, info, key_word: str = "") -> str:
            return key_word

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(
        schema,
        '{user(keyWord: "111")}',
        Query(x=1),
        middleware=TypedGraphqlMiddlewareManager(),
    )
    assert result.data == {"user": "111"}
    assert result.errors is None


def test_resolve_with_positional_argument():
    class Query(dict):
        def resolve_user(self, info, key_word: str) -> str:
            return key_word

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(
        schema,
        '{user(keyWord: "111")}',
        Query(x=1),
        middleware=TypedGraphqlMiddlewareManager(),
    )
    assert result.data == {"user": "111"}
    assert result.errors is None


def test_resolve_prefix_with_long_name_object_with_data():
    class Query(dict):
        def resolve_my_user(self, info) -> str:
            return self.get("x", "")

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(
        schema, "{myUser}", Query(x=1), middleware=TypedGraphqlMiddlewareManager()
    )
    assert result.data == {"myUser": "1"}
    assert result.errors is None


def test_int():
    class Query:
        @resolver
        def user(self, info) -> int:
            return 10

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user}", Query())
    assert result.data == {"user": 10}
    assert result.errors is None
    assert str(graphql_type(Query).fields["user"].type) == "Int!"


def test_int_with_staticresolver():
    class Query:
        @staticresolver
        def user(data, info) -> int:
            return 10

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user}")
    assert result.data == {"user": 10}
    assert result.errors is None
    assert str(graphql_type(Query).fields["user"].type) == "Int!"


def test_int_with_staticmethod():
    class Query:
        @staticmethod
        @resolver
        def user(data, info) -> int:
            return 10

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user}")
    assert result.data == {"user": 10}
    assert result.errors is None
    assert str(graphql_type(Query).fields["user"].type) == "Int!"


def test_bool():
    class Query:
        @staticresolver
        def user(data, info) -> bool:
            return True

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user}")
    assert result.data == {"user": True}
    assert result.errors is None
    assert str(graphql_type(Query).fields["user"].type) == "Boolean!"


def test_expects_int():
    class Query:
        @staticresolver
        def user(data, info) -> int:
            return "xxx"  # type: ignore

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user}")
    assert result.data is None
    assert str(result.errors[0]).startswith(
        "Int cannot represent non-integer value: 'xxx'"
    )


def test_decimal():
    class Query:
        @resolver
        def user(self, info) -> Decimal:
            return Decimal("10.5")

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user}", Query())
    assert result.data == {"user": 10.5}
    assert result.errors is None
    assert str(graphql_type(Query).fields["user"].type) == "Float!"


def test_decimal_int():
    class Query:
        @resolver
        def user(self, info) -> Decimal:
            return Decimal("10")

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user}", Query())
    assert result.data == {"user": 10.0}
    assert result.errors is None
    assert str(graphql_type(Query).fields["user"].type) == "Float!"


def test_str():
    class Query:
        @staticresolver
        def user(data, info) -> str:
            return "a string!"

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user}")
    assert result.data == {"user": "a string!"}
    assert result.errors is None
    assert str(graphql_type(Query).fields["user"].type) == "String!"


def test_optional_str():
    class Query:
        @staticresolver
        def user(data, info, x: Optional[str] = None) -> str:
            return "a string!"

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user}")
    assert result.data == {"user": "a string!"}
    assert result.errors is None
    assert str(graphql_type(Query).fields["user"].type) == "String!"


def test_string_list():
    class Query:
        @staticresolver
        def user(data, info) -> List[str]:
            return ["abc", "def"]

    assert str(graphql_type(Query).fields["user"].type) == "[String!]!"

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user}")
    assert result.data == {"user": ["abc", "def"]}
    assert result.errors is None


def test_optional_string_list():
    class Query:
        @staticresolver
        def user(data, info) -> Optional[List[Optional[str]]]:
            return ["abc", "def"]

    assert str(graphql_type(Query).fields["user"].type) == "[String]"

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user}")
    assert result.data == {"user": ["abc", "def"]}
    assert result.errors is None


def test_dataclass():
    @dataclass
    class User:
        value: str

        def resolve_value(self: "User", info) -> str:
            return self.value

    class Query:
        def resolve_user(self, info) -> List[User]:
            return [User(1)]

    assert str(graphql_type(Query).fields["user"].type) == "[User!]!"
    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(
        schema, "{user { value }}", Query(), middleware=TypedGraphqlMiddlewareManager()
    )
    assert result.data == {"user": [{"value": "1"}]}
    assert result.errors is None


def test_iterable():
    class Query:
        @staticresolver
        def user(data, info) -> Iterable[str]:
            return ["abc", "def"]

    assert str(graphql_type(Query).fields["user"].type) == "[String!]!"


def test_graphql_object_type():
    Status = GraphQLObjectType(  # NOQA
        "Status",
        {
            "text": GraphQLField(
                GraphQLString, resolve=lambda data, info: data["something"]
            )
        },
    )

    class Query:
        @staticresolver
        def user(data, info) -> Status:
            return {"something": "sometext"}

    assert str(graphql_type(Query).fields["user"].type) == "Status!"

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user { text } }")
    assert result.data == {"user": {"text": "sometext"}}
    assert result.errors is None
    assert str(graphql_type(Query).fields["user"].type) == "Status!"


def test_argument():
    class Query:
        @staticresolver
        def user(data, info, add: int) -> int:
            return 1 + add

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user(add: 10)}")
    assert result.data == {"user": 11}
    assert result.errors is None


def test_optional_argument():
    class Query:
        @staticresolver
        def user(data, info, add: Optional[int] = None) -> int:
            return 1

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user}")
    assert result.data == {"user": 1}
    assert result.errors is None


def test_optional_argument_needs_default():
    class Query:
        @staticresolver
        def user(data, info, add: Optional[int]) -> int:
            return 1

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user}")
    assert result.data is None
    assert "user() missing 1 required positional argument: 'add'" in str(
        result.errors[0]
    )


def test_mutation():
    class Query:
        @staticresolver
        def enabled(data, info) -> bool:
            return True

    class Mutation:
        @staticresolver
        def save(data, info) -> bool:
            return True

    schema = GraphQLSchema(query=graphql_type(Query), mutation=graphql_type(Mutation))
    result = graphql_sync(schema, "mutation {save}")
    assert result.data == {"save": True}


def test_sub_selection():
    class User(TypedDict):
        _value: int

        @staticresolver
        def value(d: "User", info) -> str:
            return d["_value"]

    class Query:
        @staticresolver
        def user(data, info) -> User:
            return User({"_value": "xxx"})

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user {value}}")
    assert result.data == {"user": {"value": "xxx"}}


def test_auto_camelcase_attribute():
    class User(dict):
        @staticresolver
        def my_value(d, info) -> str:
            return d["value"]

    class Query:
        @staticresolver
        def user(data, info) -> User:
            return User({"value": "xxx"})

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{user {myValue}}")
    assert result.data == {"user": {"myValue": "xxx"}}


def test_auto_camelcase_argument():
    class User(dict):
        @staticresolver
        def value(data, info, phone_number: str = "") -> str:
            return "zzz"

    class Query:
        @staticresolver
        def user(data, info) -> User:
            return User({"value": "xxx"})

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, '{user {value(phoneNumber: "100")}}')
    assert result.data == {"user": {"value": "zzz"}}


def my_wrapper(func):
    @wraps(func)
    def wrapper(data, info, **kwargs):
        return func(data, info, **kwargs)

    return wrapper


def test_decorated_attribute_works_fine():
    @dataclass
    class User:
        value: str

        @staticresolver
        @my_wrapper
        def value(data, info, phonenumber: str = "") -> str:
            return "zzz"

    class Query:
        @staticresolver
        def user(data, info) -> User:
            return User(**{"value": "xxx"})

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, '{user {value(phonenumber: "100")}}')
    assert result.data == {"user": {"value": "zzz"}}


def test_osupports_default_argument_on_get_method():
    class User(TypedDict):
        @staticresolver
        def value(data, info, phonenumber: str = "") -> str:
            return data.get("valuex", "xxx")

    class Query:
        @staticresolver
        def user(data, info) -> User:
            return User({"value": "123"})

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, '{user {value(phonenumber: "100")}}')
    assert result.data == {"user": {"value": "xxx"}}


def test_object_type_can_be_referenced_more_than_once():
    @dataclass
    class User:
        @staticresolver
        def value(data, info) -> str:
            return "xxx"

    class Query:
        @staticresolver
        def users(data, info) -> Iterable[User]:
            return [User()]

        @staticresolver
        def users2(data, info) -> Iterable[User]:
            return [User()]

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{users {value}}")
    assert result.data == {"users": [{"value": "xxx"}]}


def test_missing_return_type():
    class Query:
        @staticresolver
        def user(data, info):
            return "xxx"

    try:
        graphql_type(Query)
    except ReturnTypeMissing as e:
        assert (
            str(e)
            == "user of <class 'test_core.test_missing_return_type.<locals>.Query'> is missing return type"
        )
    else:
        raise Exception()


def test_nested():
    class Nested:
        @staticresolver
        def user(data, info, x: int) -> int:
            return 1

    class Query:
        @staticresolver
        def nested(data, info) -> Nested:
            return Nested()

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{nested {user(x: 1)}}")
    assert result.data == {"nested": {"user": 1}}
    assert result.errors is None
