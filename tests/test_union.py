"""Test Union type handling"""

from typing import Union
from dataclasses import dataclass
import pytest
from typed_graphql import graphql_type


@dataclass
class SuccessResponse:
    """Success response"""

    message: str


@dataclass
class ErrorResponse:
    """Error response"""

    error: str


class Mutation:
    """Mutation root"""

    @staticmethod
    def resolve_save_settings(data, info, value: str) -> Union[SuccessResponse, None]:
        """Save settings

        Args:
            value: The value to save
        """
        if value:
            return SuccessResponse(message="Saved")
        return None


def test_union_return_type():
    """Test that Union return types work correctly"""
    mutation_type = graphql_type(Mutation)
    assert mutation_type is not None


def test_union_as_input_argument():
    """Test Union type as input argument"""
    from graphql import GraphQLSchema, graphql_sync
    from typing import Optional, List

    @dataclass
    class ConfigInput:
        """Configuration input"""

        name: str
        value: str

    class Query:
        """Query root"""

        @staticmethod
        def resolve_hello(data, info) -> str:
            return "world"

    class Mutation2:
        """Mutation root"""

        @staticmethod
        def resolve_update_config(
            data, info, items: Optional[List[ConfigInput]]
        ) -> str:
            """Update configuration with items

            Args:
                items: The configuration items
            """
            if items:
                return f"Updated {len(items)} items"
            return "No items"

    schema = GraphQLSchema(query=graphql_type(Query), mutation=graphql_type(Mutation2))

    # Try to execute a mutation with the optional list input
    result = graphql_sync(
        schema,
        """
        mutation {
            updateConfig(items: [{name: "setting1", value: "test"}])
        }
        """,
    )
    print(result)
    assert result.errors is None or len(result.errors) == 0, f"Errors: {result.errors}"
