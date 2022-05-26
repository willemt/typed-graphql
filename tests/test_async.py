import asyncio
import time

from typing import Any, AsyncIterator, Iterable, Optional

from graphql import graphql
from graphql.type import GraphQLSchema

from typed_graphql import graphql_type, staticresolver


def get(field: str, data, info) -> Optional[Any]:
    return data.get(field)


def strict_get(field: str, data, info) -> Any:
    return data[field]


def test_async_string_list():
    class Query:
        @staticresolver
        async def user(data, info) -> Iterable[str]:
            await asyncio.sleep(0.0)
            return iter(["abc", "def"])

    schema = GraphQLSchema(query=graphql_type(Query))
    result = asyncio.new_event_loop().run_until_complete(
        graphql(schema, "{user}")
    )
    assert result.data == {"user": ["abc", "def"]}
    assert result.errors is None


def test_async_string_list_with_snake_cased_arg():
    class Query:
        @staticresolver
        async def user(data, info, phone_number: int = 0) -> Iterable[str]:
            await asyncio.sleep(0.0)
            return iter(["abc", "def"])

    schema = GraphQLSchema(query=graphql_type(Query))
    result = asyncio.new_event_loop().run_until_complete(
        graphql(schema, "{user(phoneNumber: 10)}")
    )
    assert result.data == {"user": ["abc", "def"]}
    assert result.errors is None


def test_async_iterator():
    async def aiter(lst):
        for i in lst:
            await asyncio.sleep(0.5)
            yield i

    class Query:
        @staticresolver
        async def resolve_user(data, info) -> AsyncIterator[str]:
            await asyncio.sleep(0.5)
            return aiter(["abc", "def"])

    schema = GraphQLSchema(query=graphql_type(Query))
    result = asyncio.new_event_loop().run_until_complete(graphql(schema, "{user}"))
    print(result.errors)
    assert result.data == {"user": ["abc", "def"]}
    assert result.errors is None


def test_async_lists_resolved_in_parallel():
    class Query:
        @staticresolver
        async def user(data, info, phone_number: int = 0) -> Iterable[str]:
            await asyncio.sleep(1.0)
            return iter(["abc", "def"])

        @staticresolver
        async def xxx(data, info, phone_number: int = 0) -> Iterable[str]:
            await asyncio.sleep(1.0)
            return iter(["ghi", "jkl"])

    schema = GraphQLSchema(query=graphql_type(Query))

    t0 = time.time()
    result = asyncio.new_event_loop().run_until_complete(
        graphql(schema, "{xxx(phoneNumber: 10), user(phoneNumber: 10)}")
    )
    t1 = time.time()
    total = t1 - t0
    assert total < 1.2
    assert result.data == {'user': ['abc', 'def'], 'xxx': ['ghi', 'jkl']}
    assert result.errors is None


def test_multiple_async_lists_are_run_in_parallel():
    class User(dict):
        @staticresolver
        async def value(data, info) -> str:
            await asyncio.sleep(1.0)
            return "xxx"

        @staticresolver
        async def value2(data, info) -> str:
            await asyncio.sleep(1.0)
            return "xxx"

    class Query:
        @staticresolver
        async def users(data, info) -> Iterable[User]:
            await asyncio.sleep(0.0)
            return [User({})]

        @staticresolver
        async def users2(data, info) -> Iterable[User]:
            await asyncio.sleep(0.0)
            return [User({})]

    schema = GraphQLSchema(query=graphql_type(Query))

    t0 = time.time()
    result = asyncio.new_event_loop().run_until_complete(
        graphql(schema, "{users { value, value2 }, users2 { value, value2 } }")
    )
    t1 = time.time()
    total = t1 - t0
    assert total < 1.2
    assert result.data == {
        "users": [{"value": "xxx", "value2": "xxx"}],
        "users2": [{"value": "xxx", "value2": "xxx"}],
    }
    assert result.errors is None

