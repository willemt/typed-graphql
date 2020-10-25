typed-graphql
#############


What
----
Use python types to help create graphql schemas in less code.


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

