from typing import Any, Dict, Optional

from graphql import graphql
from graphql.type import GraphQLSchema
from graphql.pyutils import is_awaitable

from .core import TypedGraphqlMiddlewareManager


async def await_awaitables(v: Any) -> Any:
    if is_awaitable(v):
        return await await_awaitables(await v)
    elif isinstance(v, dict):
        return {k: await await_awaitables(v) for k, v in v.items()}
    elif isinstance(v, list):
        return [await await_awaitables(v) for v in v]
    else:
        return v


async def execute_async(
    schema: GraphQLSchema,
    query: str,
    root: Any = None,
    context_value: Optional[Dict[str, Any]] = None,
    variable_values: Optional[Dict[str, Any]] = None,
):
    result = await graphql(
        schema,
        query,
        root,
        context_value=context_value,
        variable_values=variable_values,
        middleware=TypedGraphqlMiddlewareManager(),
    )
    result.data = await await_awaitables(result.data)
    return result
