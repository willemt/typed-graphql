from typing import List, Optional

from typed_graphql import TypedInputGraphQLObject


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


def test_snake_case():
    class UserInput(TypedInputGraphQLObject):
        name: str
        street_address: Optional[int]

    x = UserInput.graphql_type
    assert x.fields.keys() == {"name", "streetAddress"}
