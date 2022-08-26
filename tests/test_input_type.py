import enum
from typing import List, Optional, TypedDict

from typed_graphql import graphql_input_type


class MyEnum(enum.Enum):
    RED = '1'
    BLUE = '2'
    GREEN = '3'


def test_input():
    class UserInput(TypedDict):
        name: str
        age: Optional[int]
        children: List[str]
        badges: List[List[str]]

    x = graphql_input_type(UserInput)
    assert x.fields.keys() == {"name", "age", "children", "badges"}
    assert str(x.fields["age"].type) == "Int"
    assert str(x.fields["badges"].type) == "[[String!]!]!"
    assert str(x.fields["children"].type) == "[String!]!"
    assert str(x.fields["name"].type) == "String!"


def test_nested_input():
    class AddressInput(TypedDict):
        name: str

    class UserInput(TypedDict):
        name: str
        address: AddressInput

    x = graphql_input_type(UserInput)
    assert x.fields.keys() == {"name", "address"}
    assert str(x.fields["name"].type) == "String!"
    assert str(x.fields["address"].type) == "AddressInput!"


def test_snake_case():
    class UserInput(TypedDict):
        name: str
        street_address: Optional[int]

    x = graphql_input_type(UserInput)
    assert x.fields.keys() == {"name", "streetAddress"}


def test_enum():
    class UserInput(TypedDict):
        name: str
        usertype: MyEnum

    x = graphql_input_type(UserInput)
    assert x.fields.keys() == {"name", "usertype"}
    assert str(x.fields["usertype"].type) == "MyEnum!"


def test_list_of_typeddicts():
    class KeyInput(TypedDict):
        key: str
        value: str

    class UserInput(TypedDict):
        attrs: List[KeyInput]

    x = graphql_input_type(UserInput)
    assert x.fields.keys() == {"attrs"}
    assert str(x.fields["attrs"].type) == "[KeyInput!]!"


def test_optional_typeddict():
    class KeyInput(TypedDict):
        key: str
        value: str

    class UserInput(TypedDict):
        attrs: Optional[KeyInput]

    x = graphql_input_type(UserInput)
    assert x.fields.keys() == {"attrs"}
    assert str(x.fields["attrs"].type) == "KeyInput"
