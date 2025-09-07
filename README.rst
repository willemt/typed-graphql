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
3. **Minimal footprint**: typed-graphql is significantly smaller than other GraphQL libraries.

Library Size Comparison
-----------------------

typed-graphql has a much smaller installed size compared to other popular GraphQL libraries:

.. code-block::

   Library Size Comparison (installed packages):
   
   typed-graphql     ██ 48.4 KB    (1.0x)
   graphene          ████████████████████████████████████████ 992.4 KB   (20.5x larger)
   strawberry-graphql ████████████████████████████████████████████████████████████████████████████████████████████ 2.2 MB (47.1x larger)

This makes typed-graphql ideal for:

- **Serverless environments** where package size affects cold start times
- **Lightweight applications** that want minimal dependencies
- **Docker images** where every KB matters for deployment speed


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
   from typed_graphql import graphql_type, staticresolver

   class Query:
       @staticresolver
       def hello(data, info) -> str:
           return 'World'

   schema = GraphQLSchema(query=graphql_type(Query))


Features
--------

Python datetime to "Datetime" scalar

.. code-block:: python
   :class: ignore

   from graphql import graphql_sync

    @dataclass
    class User:
        login: datetime
        created: datetime

    class Query:
        def resolve_user(self, info) -> List[User]:
            return [
                User(
                    datetime(2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                    datetime(2019, 1, 1, 1, 1, 1, tzinfo=timezone.utc),
                )
            ]

Python date to "Date" scalar


.. code-block:: python
   :class: ignore


    @dataclass
    class User:
        login: date
        created: date

    class Query:
        def resolve_user(self, info) -> List[User]:
            return [
                User(
                    date(2020, 1, 1),
                    date(2019, 1, 1),
                )
            ]


Native Python Enums


.. code-block:: python
   :class: ignore

   class Status(enum.Enum):
        OFFLINE = "offline"
        ONLINE = "online"
        DORMANT = "dormant"


    @dataclass
    class User:
        status: Status

    class Query:
        def resolve_user(self, info) -> List[User]:
            return [User(Status.OFFLINE), User(Status.ONLINE)]


Argument defaults


.. code-block:: python
   :class: ignore

    @dataclass
    class User:
        str: Name

    class Query:
        @staticresolver
        def user(data, info, phone_number: Optional[str] = "000") -> List[User]:
            return User("test")


Docstrings


.. code-block:: python
   :class: ignore

    @dataclass
    class User:
        """A user agent"""

        value: str

    class Query:
        def resolve_user(self, info, pk: str) -> List[User]:
            """
            :param pk: The primary key
            """
            return [User("1")]


Installation
------------
.. code-block:: bash
   :class: ignore

   pip install typed-graphql


Philosophy
----------

1. Not a framework. If you want to do something off-script, go for it
2. Python type driven GraphQL schemas
3. Use Python builtins as much as possible (ie. dataclass, dict, TypedDict)
4. Be a thin layer over graphql-core

Example
-------
.. code-block:: python
   :class: ignore

   from functools import partial
   from typing import Any, List, Optional, TypedDict

   from graphql import graphql_sync
   from graphql.type import GraphQLSchema

   from typed_graphql import graphql_type, staticresolver


   class User(TypedDict):

       # Regular method
       @staticresolver
       def name(data, info) -> str:
           return data.get("name", "") + "1"

       # Optional respects not null types
       # Auto camelCases the attribute
       @staticresolver
       def optional_name(data, info) -> Optional[str]:
           return data.get("name", "") + "1"

       # Method with typed argument
       @staticresolver
       def addresses(data, info, limit: int) -> List[str]:
           return ["address1", "address2"]


   class Query:
       @staticresolver
       def users(data, info) -> List[User]:
           return [User(**{"name": "xxx", "status": False, "rate": 0.1})]


   query = graphql_type(Query)
   schema = GraphQLSchema(query=graphql_type(Query))

   QUERY = """
   {
       users {
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
               "name": "xxx1",
               "optionalName": "xxx1",
               "addresses": ["address1", "address2"],
           }
       ]
   }
   assert result.errors is None

