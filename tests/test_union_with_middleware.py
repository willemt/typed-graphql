"""Test Union type handling with middleware"""

from typing import Union, Optional, List
from dataclasses import dataclass
from graphql import GraphQLSchema, graphql_sync
from typed_graphql import graphql_type
from typed_graphql.core import TypedGraphqlMiddlewareManager


@dataclass
class MetadataInput:
    """Metadata input"""

    value: str


@dataclass
class SettingsInput:
    """Settings input with Union field"""

    name: str
    # This Union field inside the input type tests Optional handling
    metadata: Union[MetadataInput, None]


@dataclass
class ConfigInput:
    """Config input with Union list field"""

    items: Union[List[MetadataInput], None]


class Query:
    """Query root"""

    @staticmethod
    def resolve_hello(data, info) -> str:
        return "world"


class Mutation:
    """Mutation root"""

    @staticmethod
    def resolve_update_settings(data, info, settings: SettingsInput) -> str:
        """Update settings

        Args:
            settings: The settings with union field
        """
        return f"Updated: {settings.name}"

    @staticmethod
    def resolve_save_config(data, info, config: ConfigInput) -> str:
        """Save configuration with list union field

        Args:
            config: Config with union list field
        """
        return "Saved"


def test_union_field_inside_input_type():
    """Test Union field inside an input type WITHOUT middleware

    Without middleware, inputs are not hydrated into dataclass instances,
    so they remain as dicts. This test verifies the schema builds correctly.
    """
    schema = GraphQLSchema(query=graphql_type(Query), mutation=graphql_type(Mutation))

    # Schema should build successfully with Union fields in input types
    assert schema is not None

    # Note: Without middleware, execution will receive dicts instead of dataclass instances
    # This is expected behavior - use TypedGraphqlMiddlewareManager for automatic hydration


def test_union_list_field_inside_input_type():
    """Test Union[List, None] field inside an input type"""
    schema = GraphQLSchema(query=graphql_type(Query), mutation=graphql_type(Mutation))

    result = graphql_sync(
        schema,
        """
        mutation {
            saveConfig(config: {items: [{value: "test"}]})
        }
        """,
    )
    print(f"Result: {result}")
    assert result.errors is None or len(result.errors) == 0, f"Errors: {result.errors}"


def test_with_execute_middleware():
    """Test with TypedGraphqlMiddlewareManager

    This test reproduces the 'Cannot instantiate typing.Union' error
    that occurs when using middleware with Optional fields in input types.
    """
    schema = GraphQLSchema(query=graphql_type(Query), mutation=graphql_type(Mutation))

    result = graphql_sync(
        schema,
        """
        mutation {
            updateSettings(settings: {name: "config1", metadata: {value: "test"}})
        }
        """,
        middleware=TypedGraphqlMiddlewareManager(),
    )
    print(f"Result with middleware: {result}")
    assert result.errors is None or len(result.errors) == 0, f"Errors: {result.errors}"
