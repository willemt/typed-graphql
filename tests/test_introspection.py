from dataclasses import dataclass
from typing import Any, Iterable, List, Optional, Tuple, TypedDict

from graphql import graphql_sync
from graphql.type import GraphQLField, GraphQLSchema, GraphQLString, GraphQLObjectType

from typed_graphql import (
    ReturnTypeMissing,
    TypedGraphqlMiddlewareManager,
    graphql_type,
    resolver,
    staticresolver,
)

INTROSPECTION = """
   query IntrospectionQuery {
      __schema {
        queryType { name }
        mutationType { name }
        subscriptionType { name }
        types {
          ...FullType
        }
        directives {
          name
          description
          locations
          args {
            ...InputValue
          }
        }
      }
    }

    fragment FullType on __Type {
      kind
      name
      description
      fields(includeDeprecated: true) {
        name
        description
        args {
          ...InputValue
        }
        type {
          ...TypeRef
        }
        isDeprecated
        deprecationReason
      }
      inputFields {
        ...InputValue
      }
      interfaces {
        ...TypeRef
      }
      enumValues(includeDeprecated: true) {
        name
        description
        isDeprecated
        deprecationReason
      }
      possibleTypes {
        ...TypeRef
      }
    }

    fragment InputValue on __InputValue {
      name
      description
      type { ...TypeRef }
      defaultValue
    }

    fragment TypeRef on __Type {
      kind
      name
      ofType {
        kind
        name
        ofType {
          kind
          name
          ofType {
            kind
            name
            ofType {
              kind
              name
              ofType {
                kind
                name
                ofType {
                  kind
                  name
                  ofType {
                    kind
                    name
                  }
                }
              }
            }
          }
        }
      }
    }
"""


def test_introspection_query():
    @dataclass
    class User:
        @staticresolver
        def value(data, info) -> str:
            return "xxx"

    class Query:
        @staticresolver
        def users(data, info) -> Iterable[User]:
            return [User()]

    schema = GraphQLSchema(query=graphql_type(Query))
    result = graphql_sync(
        schema, INTROSPECTION, middleware=TypedGraphqlMiddlewareManager()
    )
    assert result.data == {
        "__schema": {
            "directives": [
                {
                    "args": [
                        {
                            "defaultValue": None,
                            "description": "Included when true.",
                            "name": "if",
                            "type": {
                                "kind": "NON_NULL",
                                "name": None,
                                "ofType": {
                                    "kind": "SCALAR",
                                    "name": "Boolean",
                                    "ofType": None,
                                },
                            },
                        }
                    ],
                    "description": "Directs the executor to include "
                    "this field or fragment only when "
                    "the `if` argument is true.",
                    "locations": ["FIELD", "FRAGMENT_SPREAD", "INLINE_FRAGMENT"],
                    "name": "include",
                },
                {
                    "args": [
                        {
                            "defaultValue": None,
                            "description": "Skipped when true.",
                            "name": "if",
                            "type": {
                                "kind": "NON_NULL",
                                "name": None,
                                "ofType": {
                                    "kind": "SCALAR",
                                    "name": "Boolean",
                                    "ofType": None,
                                },
                            },
                        }
                    ],
                    "description": "Directs the executor to skip "
                    "this field or fragment when the "
                    "`if` argument is true.",
                    "locations": ["FIELD", "FRAGMENT_SPREAD", "INLINE_FRAGMENT"],
                    "name": "skip",
                },
                {
                    "args": [
                        {
                            "defaultValue": '"No longer supported"',
                            "description": "Explains why this "
                            "element was "
                            "deprecated, usually "
                            "also including a "
                            "suggestion for how to "
                            "access supported "
                            "similar data. "
                            "Formatted using the "
                            "Markdown syntax, as "
                            "specified by "
                            "[CommonMark](https://commonmark.org/).",
                            "name": "reason",
                            "type": {
                                "kind": "SCALAR",
                                "name": "String",
                                "ofType": None,
                            },
                        }
                    ],
                    "description": "Marks an element of a GraphQL "
                    "schema as no longer supported.",
                    "locations": [
                        "FIELD_DEFINITION",
                        "ARGUMENT_DEFINITION",
                        "INPUT_FIELD_DEFINITION",
                        "ENUM_VALUE",
                    ],
                    "name": "deprecated",
                },
                {
                    "args": [
                        {
                            "defaultValue": None,
                            "description": "The URL that specifies "
                            "the behavior of this "
                            "scalar.",
                            "name": "url",
                            "type": {
                                "kind": "NON_NULL",
                                "name": None,
                                "ofType": {
                                    "kind": "SCALAR",
                                    "name": "String",
                                    "ofType": None,
                                },
                            },
                        }
                    ],
                    "description": "Exposes a URL that specifies the "
                    "behavior of this scalar.",
                    "locations": ["SCALAR"],
                    "name": "specifiedBy",
                },
            ],
            "mutationType": None,
            "queryType": {"name": "Query"},
            "subscriptionType": None,
            "types": [
                {
                    "description": None,
                    "enumValues": None,
                    "fields": [
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "users",
                            "type": {
                                "kind": "NON_NULL",
                                "name": None,
                                "ofType": {
                                    "kind": "LIST",
                                    "name": None,
                                    "ofType": {
                                        "kind": "NON_NULL",
                                        "name": None,
                                        "ofType": {
                                            "kind": "OBJECT",
                                            "name": "User",
                                            "ofType": None,
                                        },
                                    },
                                },
                            },
                        }
                    ],
                    "inputFields": None,
                    "interfaces": [],
                    "kind": "OBJECT",
                    "name": "Query",
                    "possibleTypes": None,
                },
                {
                    "description": "User()",
                    "enumValues": None,
                    "fields": [
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "value",
                            "type": {
                                "kind": "NON_NULL",
                                "name": None,
                                "ofType": {
                                    "kind": "SCALAR",
                                    "name": "String",
                                    "ofType": None,
                                },
                            },
                        }
                    ],
                    "inputFields": None,
                    "interfaces": [],
                    "kind": "OBJECT",
                    "name": "User",
                    "possibleTypes": None,
                },
                {
                    "description": "The `String` scalar type represents "
                    "textual data, represented as UTF-8 "
                    "character sequences. The String type "
                    "is most often used by GraphQL to "
                    "represent free-form human-readable "
                    "text.",
                    "enumValues": None,
                    "fields": None,
                    "inputFields": None,
                    "interfaces": None,
                    "kind": "SCALAR",
                    "name": "String",
                    "possibleTypes": None,
                },
                {
                    "description": "The `Boolean` scalar type represents "
                    "`true` or `false`.",
                    "enumValues": None,
                    "fields": None,
                    "inputFields": None,
                    "interfaces": None,
                    "kind": "SCALAR",
                    "name": "Boolean",
                    "possibleTypes": None,
                },
                {
                    "description": "A GraphQL Schema defines the "
                    "capabilities of a GraphQL server. It "
                    "exposes all available types and "
                    "directives on the server, as well as "
                    "the entry points for query, mutation, "
                    "and subscription operations.",
                    "enumValues": None,
                    "fields": [
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "description",
                            "type": {
                                "kind": "SCALAR",
                                "name": "String",
                                "ofType": None,
                            },
                        },
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": "A list of all types "
                            "supported by this server.",
                            "isDeprecated": False,
                            "name": "types",
                            "type": {
                                "kind": "NON_NULL",
                                "name": None,
                                "ofType": {
                                    "kind": "LIST",
                                    "name": None,
                                    "ofType": {
                                        "kind": "NON_NULL",
                                        "name": None,
                                        "ofType": {
                                            "kind": "OBJECT",
                                            "name": "__Type",
                                            "ofType": None,
                                        },
                                    },
                                },
                            },
                        },
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": "The type that query "
                            "operations will be rooted "
                            "at.",
                            "isDeprecated": False,
                            "name": "queryType",
                            "type": {
                                "kind": "NON_NULL",
                                "name": None,
                                "ofType": {
                                    "kind": "OBJECT",
                                    "name": "__Type",
                                    "ofType": None,
                                },
                            },
                        },
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": "If this server supports "
                            "mutation, the type that "
                            "mutation operations will "
                            "be rooted at.",
                            "isDeprecated": False,
                            "name": "mutationType",
                            "type": {
                                "kind": "OBJECT",
                                "name": "__Type",
                                "ofType": None,
                            },
                        },
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": "If this server support "
                            "subscription, the type "
                            "that subscription "
                            "operations will be rooted "
                            "at.",
                            "isDeprecated": False,
                            "name": "subscriptionType",
                            "type": {
                                "kind": "OBJECT",
                                "name": "__Type",
                                "ofType": None,
                            },
                        },
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": "A list of all directives "
                            "supported by this server.",
                            "isDeprecated": False,
                            "name": "directives",
                            "type": {
                                "kind": "NON_NULL",
                                "name": None,
                                "ofType": {
                                    "kind": "LIST",
                                    "name": None,
                                    "ofType": {
                                        "kind": "NON_NULL",
                                        "name": None,
                                        "ofType": {
                                            "kind": "OBJECT",
                                            "name": "__Directive",
                                            "ofType": None,
                                        },
                                    },
                                },
                            },
                        },
                    ],
                    "inputFields": None,
                    "interfaces": [],
                    "kind": "OBJECT",
                    "name": "__Schema",
                    "possibleTypes": None,
                },
                {
                    "description": "The fundamental unit of any GraphQL "
                    "Schema is the type. There are many "
                    "kinds of types in GraphQL as "
                    "represented by the `__TypeKind` "
                    "enum.\n"
                    "\n"
                    "Depending on the kind of a type, "
                    "certain fields describe information "
                    "about that type. Scalar types provide "
                    "no information beyond a name, "
                    "description and optional "
                    "`specifiedByURL`, while Enum types "
                    "provide their values. Object and "
                    "Interface types provide the fields "
                    "they describe. Abstract types, Union "
                    "and Interface, provide the Object "
                    "types possible at runtime. List and "
                    "NonNull types compose other types.",
                    "enumValues": None,
                    "fields": [
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "kind",
                            "type": {
                                "kind": "NON_NULL",
                                "name": None,
                                "ofType": {
                                    "kind": "ENUM",
                                    "name": "__TypeKind",
                                    "ofType": None,
                                },
                            },
                        },
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "name",
                            "type": {
                                "kind": "SCALAR",
                                "name": "String",
                                "ofType": None,
                            },
                        },
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "description",
                            "type": {
                                "kind": "SCALAR",
                                "name": "String",
                                "ofType": None,
                            },
                        },
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "specifiedByURL",
                            "type": {
                                "kind": "SCALAR",
                                "name": "String",
                                "ofType": None,
                            },
                        },
                        {
                            "args": [
                                {
                                    "defaultValue": "false",
                                    "description": None,
                                    "name": "includeDeprecated",
                                    "type": {
                                        "kind": "SCALAR",
                                        "name": "Boolean",
                                        "ofType": None,
                                    },
                                }
                            ],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "fields",
                            "type": {
                                "kind": "LIST",
                                "name": None,
                                "ofType": {
                                    "kind": "NON_NULL",
                                    "name": None,
                                    "ofType": {
                                        "kind": "OBJECT",
                                        "name": "__Field",
                                        "ofType": None,
                                    },
                                },
                            },
                        },
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "interfaces",
                            "type": {
                                "kind": "LIST",
                                "name": None,
                                "ofType": {
                                    "kind": "NON_NULL",
                                    "name": None,
                                    "ofType": {
                                        "kind": "OBJECT",
                                        "name": "__Type",
                                        "ofType": None,
                                    },
                                },
                            },
                        },
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "possibleTypes",
                            "type": {
                                "kind": "LIST",
                                "name": None,
                                "ofType": {
                                    "kind": "NON_NULL",
                                    "name": None,
                                    "ofType": {
                                        "kind": "OBJECT",
                                        "name": "__Type",
                                        "ofType": None,
                                    },
                                },
                            },
                        },
                        {
                            "args": [
                                {
                                    "defaultValue": "false",
                                    "description": None,
                                    "name": "includeDeprecated",
                                    "type": {
                                        "kind": "SCALAR",
                                        "name": "Boolean",
                                        "ofType": None,
                                    },
                                }
                            ],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "enumValues",
                            "type": {
                                "kind": "LIST",
                                "name": None,
                                "ofType": {
                                    "kind": "NON_NULL",
                                    "name": None,
                                    "ofType": {
                                        "kind": "OBJECT",
                                        "name": "__EnumValue",
                                        "ofType": None,
                                    },
                                },
                            },
                        },
                        {
                            "args": [
                                {
                                    "defaultValue": "false",
                                    "description": None,
                                    "name": "includeDeprecated",
                                    "type": {
                                        "kind": "SCALAR",
                                        "name": "Boolean",
                                        "ofType": None,
                                    },
                                }
                            ],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "inputFields",
                            "type": {
                                "kind": "LIST",
                                "name": None,
                                "ofType": {
                                    "kind": "NON_NULL",
                                    "name": None,
                                    "ofType": {
                                        "kind": "OBJECT",
                                        "name": "__InputValue",
                                        "ofType": None,
                                    },
                                },
                            },
                        },
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "ofType",
                            "type": {
                                "kind": "OBJECT",
                                "name": "__Type",
                                "ofType": None,
                            },
                        },
                    ],
                    "inputFields": None,
                    "interfaces": [],
                    "kind": "OBJECT",
                    "name": "__Type",
                    "possibleTypes": None,
                },
                {
                    "description": "An enum describing what kind of type "
                    "a given `__Type` is.",
                    "enumValues": [
                        {
                            "deprecationReason": None,
                            "description": "Indicates this type " "is a scalar.",
                            "isDeprecated": False,
                            "name": "SCALAR",
                        },
                        {
                            "deprecationReason": None,
                            "description": "Indicates this type "
                            "is an object. "
                            "`fields` and "
                            "`interfaces` are "
                            "valid fields.",
                            "isDeprecated": False,
                            "name": "OBJECT",
                        },
                        {
                            "deprecationReason": None,
                            "description": "Indicates this type "
                            "is an interface. "
                            "`fields`, "
                            "`interfaces`, and "
                            "`possibleTypes` are "
                            "valid fields.",
                            "isDeprecated": False,
                            "name": "INTERFACE",
                        },
                        {
                            "deprecationReason": None,
                            "description": "Indicates this type "
                            "is a union. "
                            "`possibleTypes` is a "
                            "valid field.",
                            "isDeprecated": False,
                            "name": "UNION",
                        },
                        {
                            "deprecationReason": None,
                            "description": "Indicates this type "
                            "is an enum. "
                            "`enumValues` is a "
                            "valid field.",
                            "isDeprecated": False,
                            "name": "ENUM",
                        },
                        {
                            "deprecationReason": None,
                            "description": "Indicates this type "
                            "is an input object. "
                            "`inputFields` is a "
                            "valid field.",
                            "isDeprecated": False,
                            "name": "INPUT_OBJECT",
                        },
                        {
                            "deprecationReason": None,
                            "description": "Indicates this type "
                            "is a list. `ofType` "
                            "is a valid field.",
                            "isDeprecated": False,
                            "name": "LIST",
                        },
                        {
                            "deprecationReason": None,
                            "description": "Indicates this type "
                            "is a non-null. "
                            "`ofType` is a valid "
                            "field.",
                            "isDeprecated": False,
                            "name": "NON_NULL",
                        },
                    ],
                    "fields": None,
                    "inputFields": None,
                    "interfaces": None,
                    "kind": "ENUM",
                    "name": "__TypeKind",
                    "possibleTypes": None,
                },
                {
                    "description": "Object and Interface types are "
                    "described by a list of Fields, each "
                    "of which has a name, potentially a "
                    "list of arguments, and a return type.",
                    "enumValues": None,
                    "fields": [
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "name",
                            "type": {
                                "kind": "NON_NULL",
                                "name": None,
                                "ofType": {
                                    "kind": "SCALAR",
                                    "name": "String",
                                    "ofType": None,
                                },
                            },
                        },
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "description",
                            "type": {
                                "kind": "SCALAR",
                                "name": "String",
                                "ofType": None,
                            },
                        },
                        {
                            "args": [
                                {
                                    "defaultValue": "false",
                                    "description": None,
                                    "name": "includeDeprecated",
                                    "type": {
                                        "kind": "SCALAR",
                                        "name": "Boolean",
                                        "ofType": None,
                                    },
                                }
                            ],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "args",
                            "type": {
                                "kind": "NON_NULL",
                                "name": None,
                                "ofType": {
                                    "kind": "LIST",
                                    "name": None,
                                    "ofType": {
                                        "kind": "NON_NULL",
                                        "name": None,
                                        "ofType": {
                                            "kind": "OBJECT",
                                            "name": "__InputValue",
                                            "ofType": None,
                                        },
                                    },
                                },
                            },
                        },
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "type",
                            "type": {
                                "kind": "NON_NULL",
                                "name": None,
                                "ofType": {
                                    "kind": "OBJECT",
                                    "name": "__Type",
                                    "ofType": None,
                                },
                            },
                        },
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "isDeprecated",
                            "type": {
                                "kind": "NON_NULL",
                                "name": None,
                                "ofType": {
                                    "kind": "SCALAR",
                                    "name": "Boolean",
                                    "ofType": None,
                                },
                            },
                        },
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "deprecationReason",
                            "type": {
                                "kind": "SCALAR",
                                "name": "String",
                                "ofType": None,
                            },
                        },
                    ],
                    "inputFields": None,
                    "interfaces": [],
                    "kind": "OBJECT",
                    "name": "__Field",
                    "possibleTypes": None,
                },
                {
                    "description": "Arguments provided to Fields or "
                    "Directives and the input fields of an "
                    "InputObject are represented as Input "
                    "Values which describe their type and "
                    "optionally a default value.",
                    "enumValues": None,
                    "fields": [
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "name",
                            "type": {
                                "kind": "NON_NULL",
                                "name": None,
                                "ofType": {
                                    "kind": "SCALAR",
                                    "name": "String",
                                    "ofType": None,
                                },
                            },
                        },
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "description",
                            "type": {
                                "kind": "SCALAR",
                                "name": "String",
                                "ofType": None,
                            },
                        },
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "type",
                            "type": {
                                "kind": "NON_NULL",
                                "name": None,
                                "ofType": {
                                    "kind": "OBJECT",
                                    "name": "__Type",
                                    "ofType": None,
                                },
                            },
                        },
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": "A GraphQL-formatted "
                            "string representing the "
                            "default value for this "
                            "input value.",
                            "isDeprecated": False,
                            "name": "defaultValue",
                            "type": {
                                "kind": "SCALAR",
                                "name": "String",
                                "ofType": None,
                            },
                        },
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "isDeprecated",
                            "type": {
                                "kind": "NON_NULL",
                                "name": None,
                                "ofType": {
                                    "kind": "SCALAR",
                                    "name": "Boolean",
                                    "ofType": None,
                                },
                            },
                        },
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "deprecationReason",
                            "type": {
                                "kind": "SCALAR",
                                "name": "String",
                                "ofType": None,
                            },
                        },
                    ],
                    "inputFields": None,
                    "interfaces": [],
                    "kind": "OBJECT",
                    "name": "__InputValue",
                    "possibleTypes": None,
                },
                {
                    "description": "One possible value for a given Enum. "
                    "Enum values are unique values, not a "
                    "placeholder for a string or numeric "
                    "value. However an Enum value is "
                    "returned in a JSON response as a "
                    "string.",
                    "enumValues": None,
                    "fields": [
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "name",
                            "type": {
                                "kind": "NON_NULL",
                                "name": None,
                                "ofType": {
                                    "kind": "SCALAR",
                                    "name": "String",
                                    "ofType": None,
                                },
                            },
                        },
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "description",
                            "type": {
                                "kind": "SCALAR",
                                "name": "String",
                                "ofType": None,
                            },
                        },
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "isDeprecated",
                            "type": {
                                "kind": "NON_NULL",
                                "name": None,
                                "ofType": {
                                    "kind": "SCALAR",
                                    "name": "Boolean",
                                    "ofType": None,
                                },
                            },
                        },
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "deprecationReason",
                            "type": {
                                "kind": "SCALAR",
                                "name": "String",
                                "ofType": None,
                            },
                        },
                    ],
                    "inputFields": None,
                    "interfaces": [],
                    "kind": "OBJECT",
                    "name": "__EnumValue",
                    "possibleTypes": None,
                },
                {
                    "description": "A Directive provides a way to "
                    "describe alternate runtime execution "
                    "and type validation behavior in a "
                    "GraphQL document.\n"
                    "\n"
                    "In some cases, you need to provide "
                    "options to alter GraphQL's execution "
                    "behavior in ways field arguments will "
                    "not suffice, such as conditionally "
                    "including or skipping a field. "
                    "Directives provide this by describing "
                    "additional information to the "
                    "executor.",
                    "enumValues": None,
                    "fields": [
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "name",
                            "type": {
                                "kind": "NON_NULL",
                                "name": None,
                                "ofType": {
                                    "kind": "SCALAR",
                                    "name": "String",
                                    "ofType": None,
                                },
                            },
                        },
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "description",
                            "type": {
                                "kind": "SCALAR",
                                "name": "String",
                                "ofType": None,
                            },
                        },
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "isRepeatable",
                            "type": {
                                "kind": "NON_NULL",
                                "name": None,
                                "ofType": {
                                    "kind": "SCALAR",
                                    "name": "Boolean",
                                    "ofType": None,
                                },
                            },
                        },
                        {
                            "args": [],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "locations",
                            "type": {
                                "kind": "NON_NULL",
                                "name": None,
                                "ofType": {
                                    "kind": "LIST",
                                    "name": None,
                                    "ofType": {
                                        "kind": "NON_NULL",
                                        "name": None,
                                        "ofType": {
                                            "kind": "ENUM",
                                            "name": "__DirectiveLocation",
                                            "ofType": None,
                                        },
                                    },
                                },
                            },
                        },
                        {
                            "args": [
                                {
                                    "defaultValue": "false",
                                    "description": None,
                                    "name": "includeDeprecated",
                                    "type": {
                                        "kind": "SCALAR",
                                        "name": "Boolean",
                                        "ofType": None,
                                    },
                                }
                            ],
                            "deprecationReason": None,
                            "description": None,
                            "isDeprecated": False,
                            "name": "args",
                            "type": {
                                "kind": "NON_NULL",
                                "name": None,
                                "ofType": {
                                    "kind": "LIST",
                                    "name": None,
                                    "ofType": {
                                        "kind": "NON_NULL",
                                        "name": None,
                                        "ofType": {
                                            "kind": "OBJECT",
                                            "name": "__InputValue",
                                            "ofType": None,
                                        },
                                    },
                                },
                            },
                        },
                    ],
                    "inputFields": None,
                    "interfaces": [],
                    "kind": "OBJECT",
                    "name": "__Directive",
                    "possibleTypes": None,
                },
                {
                    "description": "A Directive can be adjacent to many "
                    "parts of the GraphQL language, a "
                    "__DirectiveLocation describes one "
                    "such possible adjacencies.",
                    "enumValues": [
                        {
                            "deprecationReason": None,
                            "description": "Location adjacent to " "a query operation.",
                            "isDeprecated": False,
                            "name": "QUERY",
                        },
                        {
                            "deprecationReason": None,
                            "description": "Location adjacent to "
                            "a mutation operation.",
                            "isDeprecated": False,
                            "name": "MUTATION",
                        },
                        {
                            "deprecationReason": None,
                            "description": "Location adjacent to "
                            "a subscription "
                            "operation.",
                            "isDeprecated": False,
                            "name": "SUBSCRIPTION",
                        },
                        {
                            "deprecationReason": None,
                            "description": "Location adjacent to " "a field.",
                            "isDeprecated": False,
                            "name": "FIELD",
                        },
                        {
                            "deprecationReason": None,
                            "description": "Location adjacent to "
                            "a fragment "
                            "definition.",
                            "isDeprecated": False,
                            "name": "FRAGMENT_DEFINITION",
                        },
                        {
                            "deprecationReason": None,
                            "description": "Location adjacent to " "a fragment spread.",
                            "isDeprecated": False,
                            "name": "FRAGMENT_SPREAD",
                        },
                        {
                            "deprecationReason": None,
                            "description": "Location adjacent to "
                            "an inline fragment.",
                            "isDeprecated": False,
                            "name": "INLINE_FRAGMENT",
                        },
                        {
                            "deprecationReason": None,
                            "description": "Location adjacent to "
                            "a variable "
                            "definition.",
                            "isDeprecated": False,
                            "name": "VARIABLE_DEFINITION",
                        },
                        {
                            "deprecationReason": None,
                            "description": "Location adjacent to "
                            "a schema definition.",
                            "isDeprecated": False,
                            "name": "SCHEMA",
                        },
                        {
                            "deprecationReason": None,
                            "description": "Location adjacent to "
                            "a scalar definition.",
                            "isDeprecated": False,
                            "name": "SCALAR",
                        },
                        {
                            "deprecationReason": None,
                            "description": "Location adjacent to "
                            "an object type "
                            "definition.",
                            "isDeprecated": False,
                            "name": "OBJECT",
                        },
                        {
                            "deprecationReason": None,
                            "description": "Location adjacent to "
                            "a field definition.",
                            "isDeprecated": False,
                            "name": "FIELD_DEFINITION",
                        },
                        {
                            "deprecationReason": None,
                            "description": "Location adjacent to "
                            "an argument "
                            "definition.",
                            "isDeprecated": False,
                            "name": "ARGUMENT_DEFINITION",
                        },
                        {
                            "deprecationReason": None,
                            "description": "Location adjacent to "
                            "an interface "
                            "definition.",
                            "isDeprecated": False,
                            "name": "INTERFACE",
                        },
                        {
                            "deprecationReason": None,
                            "description": "Location adjacent to "
                            "a union definition.",
                            "isDeprecated": False,
                            "name": "UNION",
                        },
                        {
                            "deprecationReason": None,
                            "description": "Location adjacent to "
                            "an enum definition.",
                            "isDeprecated": False,
                            "name": "ENUM",
                        },
                        {
                            "deprecationReason": None,
                            "description": "Location adjacent to "
                            "an enum value "
                            "definition.",
                            "isDeprecated": False,
                            "name": "ENUM_VALUE",
                        },
                        {
                            "deprecationReason": None,
                            "description": "Location adjacent to "
                            "an input object type "
                            "definition.",
                            "isDeprecated": False,
                            "name": "INPUT_OBJECT",
                        },
                        {
                            "deprecationReason": None,
                            "description": "Location adjacent to "
                            "an input object field "
                            "definition.",
                            "isDeprecated": False,
                            "name": "INPUT_FIELD_DEFINITION",
                        },
                    ],
                    "fields": None,
                    "inputFields": None,
                    "interfaces": None,
                    "kind": "ENUM",
                    "name": "__DirectiveLocation",
                    "possibleTypes": None,
                },
            ],
        }
    }
