from dataclasses import dataclass
import enum
from typing import Any
from typing import List
from typing import Optional
from typing import TypedDict
from typing import NewType

from graphql import graphql_sync
from graphql.type import GraphQLSchema

from typed_graphql import graphql_type, staticresolver
from typed_graphql import TypedGraphqlMiddlewareManager


def get(field: str, data, info) -> Optional[Any]:
    return data.get(field)


def strict_get(field: str, data, info) -> Any:
    return data[field]


def test_mutation():
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
            phone_number: str = "",
            groups: Optional[List[str]] = None,
            name: Optional[str] = None,
            size: float = None,
        ) -> User:
            return User({"name": name})

    schema = GraphQLSchema(query=graphql_type(Query), mutation=graphql_type(Mutation))
    result = graphql_sync(
        schema,
        """
    mutation createUser {
        createUser(size: 100, name: "XXX", phoneNumber: "10") {
            name
        }
    }
    """,
    )
    assert result.data == {"createUser": {"name": "XXX"}}


def test_mutation_with_input_object():
    class User(dict):
        @staticresolver
        def name(d, info) -> str:
            return d["name"]

    class Query(dict):
        @staticresolver
        def user(d, info) -> str:
            return ""

    class UserInput(dict):
        id: str
        name: str

    class Mutation:
        @staticresolver
        def create_user(data, info, user: UserInput) -> User:
            return User({"name": user["name"]})

    schema = GraphQLSchema(query=graphql_type(Query), mutation=graphql_type(Mutation))
    result = graphql_sync(
        schema,
        """
    mutation createUser {
        createUser(user: {id: "xxx", name: "123"}) {
            name
        }
    }
    """,
    )
    assert result.data == {"createUser": {"name": "123"}}


def test_mutation_with_enum_input_object():
    class Colour(enum.Enum):
        RED = "1"
        BLUE = "2"
        GREEN = "3"

    class User(dict):
        @staticresolver
        def colour(d, info) -> Colour:
            return d["colour"]

    class Query:
        @staticresolver
        def user(data, info) -> str:
            return ""

    class UserInput(TypedDict):
        colour: Colour

    class Mutation:
        @staticresolver
        def create_user(data, info, user: UserInput) -> User:
            return User({"colour": user["colour"]})

    schema = GraphQLSchema(query=graphql_type(Query), mutation=graphql_type(Mutation))
    result = graphql_sync(
        schema,
        """
    mutation createUser {
        createUser(user: {colour: RED}) {
            colour
        }
    }
    """,
    )
    assert result.data == {"createUser": {"colour": "RED"}}


def test_list_of_input_types():
    class MyInput(TypedDict):
        my_input_items: List[str]
        activated: bool

    class Query:
        @staticresolver
        async def user(data, info) -> str:
            return "abc"

    class Mutation:
        @staticresolver
        async def save_user(data, info, x: List[MyInput]) -> str:
            return "abc"

    # There's no exception raised
    graphql_type(Mutation)


def test_mutation_with_dataclass_input_object():
    class Colour(enum.Enum):
        RED = "1"
        BLUE = "2"
        GREEN = "3"

    class User(dict):
        def resolve_colour(d, info) -> Colour:
            return d["colour"]

    class Query:
        @staticresolver
        def user(data, info) -> str:
            return ""

    @dataclass
    class UserInput:
        colour: Colour

    class Mutation:
        @staticresolver
        def create_user(data, info, user: UserInput) -> User:
            return User({"colour": user.colour})

    schema = GraphQLSchema(query=graphql_type(Query), mutation=graphql_type(Mutation))
    result = graphql_sync(
        schema,
        """
    mutation createUser {
        createUser(user: {colour: RED}) {
            colour
        }
    }
    """,
        middleware=TypedGraphqlMiddlewareManager(),
    )
    assert result.data == {"createUser": {"colour": "RED"}}


def test_mutation_with_nested_dataclass_input_object():
    @dataclass
    class Car:
        model: str

    class User(dict):
        def resolve_car(d, info) -> Car:
            return Car("xxx")

    class Query:
        @staticresolver
        def user(data, info) -> str:
            return ""

    @dataclass
    class UserInput:
        car: Car

    class Mutation:
        @staticresolver
        def create_user(data, info, user: UserInput) -> User:
            assert isinstance(user.car, Car)
            return User({})

    schema = GraphQLSchema(query=graphql_type(Query), mutation=graphql_type(Mutation))
    result = graphql_sync(
        schema,
        """
    mutation createUser {
        createUser(user: {car: {model: "xxx"}}) {
            car { model }
        }
    }
    """,
        middleware=TypedGraphqlMiddlewareManager(),
    )
    assert result.data == {"createUser": {"car": {"model": "xxx"}}}


def test_mutation_with_nested_list_dataclass_input_object():
    @dataclass
    class Car:
        model: str

    class User(dict):
        def resolve_cars(d, info) -> List[Car]:
            return [Car("xxx")]

    class Query:
        @staticresolver
        def user(data, info) -> str:
            return ""

    @dataclass
    class UserInput:
        cars: List[Car]

    class Mutation:
        @staticresolver
        def create_user(data, info, user: UserInput) -> User:
            assert isinstance(user.cars[0], Car)
            return User(cars=[])

    schema = GraphQLSchema(query=graphql_type(Query), mutation=graphql_type(Mutation))
    result = graphql_sync(
        schema,
        """
    mutation createUser {
        createUser(user: {cars: [{model: "xxx"}]}) {
            cars { model }
        }
    }
    """,
        middleware=TypedGraphqlMiddlewareManager(),
    )
    assert result.data == {"createUser": {"cars": [{"model": "xxx"}]}}


def test_mutation_with_dataclass_input_object_snake_case():
    class Colour(enum.Enum):
        RED = "1"
        BLUE = "2"
        GREEN = "3"

    class User(dict):
        def resolve_colour(d, info) -> Colour:
            return d["colour"]

    class Query:
        @staticresolver
        def user(data, info) -> str:
            return ""

    @dataclass
    class UserInput:
        my_colour: Colour

    class Mutation:
        @staticresolver
        def create_user(data, info, user: UserInput) -> User:
            return User({"colour": user.my_colour})

    schema = GraphQLSchema(query=graphql_type(Query), mutation=graphql_type(Mutation))
    result = graphql_sync(
        schema,
        """
    mutation createUser {
        createUser(user: {myColour: RED}) {
            colour
        }
    }
    """,
        middleware=TypedGraphqlMiddlewareManager(),
    )
    assert result.data == {"createUser": {"colour": "RED"}}


def test_input_with_newtype():
    class User(dict):
        def resolve_colour(d, info) -> str:
            return d["xxx"]

    class Query:
        @staticresolver
        def user(data, info) -> str:
            return ""

    UserInput = NewType("UserInput", str)

    class Mutation:
        @staticresolver
        def create_user(data, info, user_id: UserInput) -> User:
            return User({"xxx": user_id})

    schema = GraphQLSchema(query=graphql_type(Query), mutation=graphql_type(Mutation))
    result = graphql_sync(
        schema,
        """
    mutation createUser {
        createUser(userId: "red") {
            colour
        }
    }
    """,
        middleware=TypedGraphqlMiddlewareManager(),
    )
    print(result.errors)
    assert result.data == {"createUser": {"colour": "red"}}
