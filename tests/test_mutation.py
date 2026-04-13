import asyncio
from dataclasses import dataclass
import enum
from typing import Any
from typing import List
from typing import Optional
from typing import TypedDict
from typing import NewType

from graphql import graphql
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
        createUser(user: {cars: [{model: "abc"}, {model: "xxx"}]}) {
            cars { model }
        }
    }
    """,
        middleware=TypedGraphqlMiddlewareManager(),
    )
    assert result.data == {"createUser": {"cars": [{"model": "xxx"}]}}


def test_mutation_with_nested_list_class_input_object():
    class Car:
        model: str

        def __init__(self, model: str):
            self.model = model

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
        createUser(user: {cars: [{model: "abc"}, {model: "xxx"}]}) {
            cars { model }
        }
    }
    """,
        middleware=TypedGraphqlMiddlewareManager(),
    )
    assert result.data == {"createUser": {"cars": [{"model": "xxx"}]}}


def test_mutation_with_nested_snake_case_list_dataclass_input_object():
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
        def create_user(data, info, my_user: UserInput) -> User:
            assert isinstance(my_user.cars[0], Car)
            return User(cars=[])

    schema = GraphQLSchema(query=graphql_type(Query), mutation=graphql_type(Mutation))
    result = graphql_sync(
        schema,
        """
    mutation createUser {
        createUser(myUser: {cars: [{model: "abc"}, {model: "xxx"}]}) {
            cars { model }
        }
    }
    """,
        middleware=TypedGraphqlMiddlewareManager(),
    )
    assert result.data == {"createUser": {"cars": [{"model": "xxx"}]}}


def test_async_mutation_with_nested_list_dataclass_input_object():
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
        async def create_user(data, info, user: UserInput) -> User:
            assert isinstance(user.cars[0], Car)
            return User(cars=[])

    schema = GraphQLSchema(query=graphql_type(Query), mutation=graphql_type(Mutation))
    result = asyncio.new_event_loop().run_until_complete(
        graphql(
            schema,
            """
    mutation createUser {
        createUser(user: {cars: [{model: "abc"}, {model: "xxx"}]}) {
            cars { model }
        }
    }
    """,
            middleware=TypedGraphqlMiddlewareManager(),
        )
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


def test_optional_list_of_optional_input_objects():
    """Optional[list[Optional[T]]] on an input field must hydrate correctly."""

    @dataclass
    class TagInput:
        name: Optional[str] = None

    @dataclass
    class ItemInput:
        title: Optional[str] = None
        tags: Optional[list[Optional[TagInput]]] = None

    class Query:
        @staticresolver
        def ping(data, info) -> str:
            return "pong"

    class Mutation:
        @staticresolver
        def create_item(data, info, item: Optional[ItemInput] = None) -> Optional[str]:
            if item is None:
                return None
            tag_names = [t.name for t in (item.tags or []) if t is not None]
            return f"{item.title}:{','.join(tag_names)}"

    schema = GraphQLSchema(query=graphql_type(Query), mutation=graphql_type(Mutation))
    middleware = TypedGraphqlMiddlewareManager()

    # Without tags — must not crash
    r = graphql_sync(
        schema,
        'mutation { createItem(item: {title: "hello"}) }',
        middleware=middleware,
    )
    assert r.errors is None
    assert r.data == {"createItem": "hello:"}

    # With tags — previously raised "Cannot instantiate typing.Union"
    r = graphql_sync(
        schema,
        'mutation { createItem(item: {title: "hello", tags: [{name: "foo"}, {name: "bar"}]}) }',
        middleware=middleware,
    )
    assert r.errors is None
    assert r.data == {"createItem": "hello:foo,bar"}


def test_deeply_nested_optional_list_input():
    """Optional[list[Optional[list[Optional[T]]]]] — arbitrary nesting depth."""

    @dataclass
    class Inner:
        x: int = 0

    @dataclass
    class Outer:
        items: Optional[list[Optional[list[Optional[Inner]]]]] = None

    class Query:
        @staticresolver
        def ping(data, info) -> str:
            return "pong"

    class Mutation:
        @staticresolver
        def run(data, info, outer: Optional[Outer] = None) -> Optional[str]:
            if outer is None or outer.items is None:
                return "none"
            total = sum(
                inner.x
                for row in outer.items
                if row is not None
                for inner in row
                if inner is not None
            )
            return str(total)

    schema = GraphQLSchema(query=graphql_type(Query), mutation=graphql_type(Mutation))
    r = graphql_sync(
        schema,
        "mutation { run(outer: {items: [[{x: 1}, {x: 2}], [{x: 3}]]}) }",
        middleware=TypedGraphqlMiddlewareManager(),
    )
    assert r.errors is None
    assert r.data == {"run": "6"}
