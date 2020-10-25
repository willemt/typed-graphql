import inspect
from typing import Callable, TypeVar

from graphql.pyutils import camel_to_snake, snake_to_camel
from graphql.type import (
    GraphQLArgument,
    GraphQLBoolean as Boolean,
    GraphQLField as Field,
    GraphQLFloat as Float,
    GraphQLInt as Int,
    GraphQLList,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLString as String,
)


T = TypeVar('T')

SimpleResolver = Callable[[dict, dict], T]


RESERVED_ARGUMENT_NAMES = set(["data", "info", "return"])


class classproperty(object):  # NOQA
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)


class TypedGraphQLObject:
    graphql_object_class = GraphQLObjectType

    def __init__(self, data: dict = None):
        self.data = data or {}

    def __getitem__(self, x: str):
        return self.data[x]

    def get(self, x: str):
        return self.data.get(x)

    def __getattribute__(self, name):
        py_name = camel_to_snake(name)
        return super().__getattribute__(py_name)

    @classproperty
    def graphql_type(cls):

        fields = {}

        public_attrs = (
            (attr_name, y)
            for attr_name, y in cls.__dict__.items()
            if not attr_name.startswith("_")
        )

        for attr_name, attr in public_attrs:
            if attr_name.startswith("_"):
                continue

            signature = inspect.signature(attr)
            params = list(signature.parameters.items())

            # if params[0][0] != "data":
            #     raise Exception("1st parameter of function should be 'data'")
            # if params[1][0] != "info":
            #     raise Exception("2nd parameter of function should be 'info'")

            args = {
                param_name: GraphQLArgument(
                    python_type_to_graphql_type(param.annotation)
                )
                for param_name, param in params[2:]
            }

            try:
                return_type = cls.__annotations__[attr_name].__args__[-1]
            except (AttributeError, KeyError):
                return_type = signature.return_annotation
                # return_type = attr.__annotations__["return"]

            field = Field(
                python_type_to_graphql_type(return_type), args=args, resolve=attr
            )
            field_name = snake_to_camel(attr_name, upper=False)
            fields[field_name] = field

        return cls.graphql_object_class(cls.__name__, fields)


def python_type_to_graphql_type(t, nonnull=True):
    if str(t).startswith("typing.List"):
        assert len(t.__args__) == 1
        return GraphQLList(python_type_to_graphql_type(t.__args__[0], nonnull=True))
    if str(t).startswith("graphql.type.definition.GraphQLList"):
        assert len(t.__args__) == 1
        return GraphQLList(python_type_to_graphql_type(t.__args__[0], nonnull=True))
    elif str(t).startswith("typing.Union"):
        if len(t.__args__) == 2:
            if issubclass(t.__args__[1], type(None)):
                return python_type_to_graphql_type(t.__args__[0], nonnull=False)
            else:
                raise Exception
        else:
            raise Exception
    elif isinstance(t, GraphQLObjectType):
        return t
    elif issubclass(t, TypedGraphQLObject):
        if nonnull:
            return GraphQLNonNull(t.graphql_type)
        return t.graphql_type
    elif issubclass(t, str):
        if nonnull:
            return GraphQLNonNull(String)
        return String
    elif issubclass(t, bool):
        if nonnull:
            return GraphQLNonNull(Boolean)
        return Boolean
    elif issubclass(t, int):
        if nonnull:
            return GraphQLNonNull(Int)
        return Int
    elif issubclass(t, float):
        if nonnull:
            return GraphQLNonNull(Float)
        return Float
    else:
        raise Exception(t)
