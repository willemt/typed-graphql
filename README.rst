typed-graphql
#############


What
----
What if writing types for your GraphQL resolvers resulted in you defining your schema?

Use Python types to create GraphQL schemas in less code.

typed-graphl is a thin layer over graphql-core.

Why
---
1. Much of your schema can be defined by using types, reducing code size.
2. It's more flexible to use a thin layer over graphql-core, as opposed to a large framework.


Graphene:

.. code-block:: python
   :class: ignore

   import graphene

   class Query(graphene.ObjectType):
       hello = graphene.String(description='A typical hello world')

       def resolve_hello(self, info):
           return 'World'

   schema = graphene.Schema(query=Query)


Typed-graphql:

.. code-block:: python
   :class: ignore

   from graphql import graphql_sync
   from graphql.type import GraphQLSchema
   from typed_graphql import SimpleResolver, TypedGraphQLObject

   class Query(TypedGraphQLObject):
       def hello(data, info) -> str:
           return 'World'

   schema = GraphQLSchema(query=Query.graphql_type)


Installation
------------
.. code-block:: bash
   :class: ignore

   pip install typed-graphql

Example
-------
.. code-block:: python
   :class: ignore

   from functools import partial
   from typing import Any, List, Optional

   from graphql import graphql_sync
   from graphql.type import GraphQLSchema

   from typed_graphql import SimpleResolver, TypedGraphQLObject


   def get(field: str, data, info) -> Optional[Any]:
       return data.get(field)


   def strict_get(field: str, data, info) -> Any:
       return data[field]


   class User(TypedGraphQLObject):

       # Regular method
       def name(data, info) -> str:
           return data.get("name") + "1"

       # Optional respects not null types
       # Auto camelCases the attribute
       def optional_name(data, info) -> Optional[str]:
           return data.get("name") + "1"

       # Method with typed argument
       def addresses(data, info, limit: int) -> List[str]:
           return ["address1", "address2"]

       # Function assignment
       enabled: SimpleResolver[bool] = partial(strict_get, "status")


   class Query(TypedGraphQLObject):
       def users(data, info) -> List[User]:
           return [User({"name": "xxx", "status": False, "rate": 0.1})]


   query = Query.graphql_type
   schema = GraphQLSchema(query=Query.graphql_type)

   QUERY = """
   {
       users {
           enabled
           name
           optionalName
           addresses(limit: 1)
       }
   }
   """

   result = graphql_sync(schema, QUERY)

   assert result.data == {
       "users": [
           {
               "enabled": False,
               "name": "xxx1",
               "optionalName": "xxx1",
               "addresses": ["address1", "address2"],
           }
       ]
   }
   assert result.errors is None

