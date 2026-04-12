"""
Tests for ForwardRef / lazy type resolution and circular type relationships.

Two root causes are exercised:

1. Infinite recursion — graphql_type() previously registered the stub AFTER
   building fields, so any recursive reference looped forever.  Fixed by
   registering a thunk-backed stub first.

2. ForwardRef crash — python_type_to_graphql_type() fell through to issubclass()
   which raises TypeError on a ForwardRef.  Fixed by an explicit ForwardRef
   handler that resolves against module globals then ctx.type_by_name.
"""

from dataclasses import dataclass
from typing import List, Optional

from graphql import graphql_sync, print_schema
from graphql.type import GraphQLSchema

from typed_graphql import GraphQLTypeConversionContext, graphql_type, staticresolver

# ---------------------------------------------------------------------------
# Module-level types — resolvable via module globals, self- and mutually
# referential.  These exercise the infinite-recursion / thunk fix.
# ---------------------------------------------------------------------------


@dataclass
class TreeNode:
    """A self-referential tree node."""

    value: str
    children: List["TreeNode"]


@dataclass
class Author:
    """An author who has written posts."""

    name: str
    posts: List["Post"]


@dataclass
class Post:
    """A post written by an author."""

    title: str
    author: Author


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_self_referential_dataclass():
    """TreeNode.children: List[TreeNode] must not recurse infinitely."""

    class Query:
        @staticresolver
        def root(data, info) -> TreeNode:
            return TreeNode(
                value="root",
                children=[TreeNode(value="child", children=[])],
            )

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{ root { value children { value } } }")
    assert result.errors is None
    assert result.data == {"root": {"value": "root", "children": [{"value": "child"}]}}


def test_self_referential_schema_shape():
    """The SDL for TreeNode must show 'children: [TreeNode!]!'."""

    class Query:
        @staticresolver
        def root(data, info) -> TreeNode:
            return TreeNode(value="root", children=[])

    schema = GraphQLSchema(query=graphql_type(Query))
    sdl = print_schema(schema)
    assert "children: [TreeNode!]!" in sdl


def test_mutual_circular_dataclasses():
    """Author ↔ Post: each dataclass references the other."""

    class Query:
        @staticresolver
        def author(data, info) -> Author:
            return Author(
                name="Alice",
                posts=[Post(title="Hello", author=Author(name="Alice", posts=[]))],
            )

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{ author { name posts { title author { name } } } }")
    assert result.errors is None
    assert result.data == {
        "author": {
            "name": "Alice",
            "posts": [{"title": "Hello", "author": {"name": "Alice"}}],
        }
    }


def test_mutual_circular_schema_shape():
    """Schema SDL must declare both Author and Post with the cross-reference fields."""

    class Query:
        @staticresolver
        def author(data, info) -> Author:
            return Author(name="Alice", posts=[])

    schema = GraphQLSchema(query=graphql_type(Query))
    sdl = print_schema(schema)
    assert "posts: [Post!]!" in sdl
    assert "author: Author!" in sdl


def test_optional_self_reference():
    """Optional[self] (nullable self-ref) must resolve to the type without NonNull."""

    @dataclass
    class LinkedListNode:
        value: int
        next: Optional["LinkedListNode"]

    class Query:
        @staticresolver
        def head(data, info) -> LinkedListNode:
            return LinkedListNode(value=1, next=LinkedListNode(value=2, next=None))

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(schema, "{ head { value next { value } } }")
    assert result.errors is None
    assert result.data == {"head": {"value": 1, "next": {"value": 2}}}

    # next must be nullable (no NonNull wrapping)
    head_type = graphql_type(Query).fields["head"].type.of_type
    assert str(head_type.fields["next"].type) == "LinkedListNode"


def test_forward_ref_via_ctx_type_by_name():
    """
    WidgetItem.collection returns Optional["WidgetCollection"] — a ForwardRef
    that cannot be resolved from WidgetItem's module globals (both are
    function-local).  The ForwardRef handler must fall back to ctx.type_by_name
    after graphql_type(WidgetCollection) has been called with the same context.
    """

    class WidgetItem:
        @staticresolver
        def item_id(data, info) -> str:
            return "item-1"

        @staticresolver
        def collection(data, info) -> Optional["WidgetCollection"]:
            return None

    class WidgetCollection:
        @staticresolver
        def collection_id(data, info) -> str:
            return "col-1"

        @staticresolver
        def items(data, info) -> List[WidgetItem]:
            return []

    ctx = GraphQLTypeConversionContext()

    # Register WidgetCollection first so it's in ctx.type_by_name when
    # WidgetItem's thunk resolves the ForwardRef('WidgetCollection').
    graphql_type(WidgetCollection, ctx=ctx)

    class Query:
        @staticresolver
        def widget_collection(data, info) -> WidgetCollection:
            return WidgetCollection()

    schema = GraphQLSchema(query=graphql_type(Query, ctx=ctx))
    result = graphql_sync(
        schema, "{ widgetCollection { collectionId items { itemId } } }"
    )
    assert result.errors is None
    assert result.data == {"widgetCollection": {"collectionId": "col-1", "items": []}}


def test_same_context_reuses_type_objects():
    """Two separate calls to graphql_type with the same ctx return the same object."""

    ctx = GraphQLTypeConversionContext()

    class Query:
        @staticresolver
        def root(data, info) -> TreeNode:
            return TreeNode(value="r", children=[])

    t1 = graphql_type(Query, ctx=ctx)
    t2 = graphql_type(Query, ctx=ctx)
    assert t1 is t2

    # Building the schema triggers the thunks, which registers nested types.
    GraphQLSchema(query=t1)
    assert "TreeNode" in ctx.type_by_name
