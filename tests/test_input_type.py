import enum
from typing import List, Optional

from typed_graphql import TypedInputGraphQLObject


class MyEnum(enum.Enum):
    RED = '1'
    BLUE = '2'
    GREEN = '3'


def test_input():
    class UserInput(TypedInputGraphQLObject):
        name: str
        age: Optional[int]
        children: List[str]
        badges: List[List[str]]

    x = UserInput.graphql_type
    assert x.fields.keys() == {"name", "age", "children", "badges"}
    assert str(x.fields["age"].type) == "Int"
    assert str(x.fields["badges"].type) == "[[String!]]"
    assert str(x.fields["children"].type) == "[String!]"
    assert str(x.fields["name"].type) == "String!"


def test_nested_input():
    class AddressInput(TypedInputGraphQLObject):
        name: str

    class UserInput(TypedInputGraphQLObject):
        name: str
        address: AddressInput

    x = UserInput.graphql_type
    assert x.fields.keys() == {"name", "address"}
    assert str(x.fields["name"].type) == "String!"
    assert str(x.fields["address"].type) == "AddressInput!"


def test_snake_case():
    class UserInput(TypedInputGraphQLObject):
        name: str
        street_address: Optional[int]

    x = UserInput.graphql_type
    assert x.fields.keys() == {"name", "streetAddress"}


def test_enum():
    class UserInput(TypedInputGraphQLObject):
        name: str
        usertype: MyEnum

    x = UserInput.graphql_type
    assert x.fields.keys() == {"name", "usertype"}
    assert str(x.fields["usertype"].type) == "MyEnum!"
