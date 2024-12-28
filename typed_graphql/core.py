import enum
import inspect
import sys
from dataclasses import fields as dataclass_fields, is_dataclass
from functools import partial, wraps
from operator import getitem
from typing import Annotated
from typing import Any
from typing import Callable
from typing import Dict
from typing import GenericAlias
from typing import List
from typing import Optional
from typing import TypeVar
from typing import cast
from typing import get_args
from typing import get_origin
from typing import get_type_hints

import docstring_parser

from graphql.execution import MiddlewareManager
from graphql.pyutils import camel_to_snake
from graphql.pyutils import snake_to_camel
from graphql.pyutils import Undefined
from graphql.type import GraphQLArgument
from graphql.type import GraphQLBoolean as Boolean
from graphql.type import GraphQLEnumType
from graphql.type import GraphQLField as Field
from graphql.type import GraphQLFloat as Float
from graphql.type import GraphQLInputField as InputField
from graphql.type import GraphQLInputObjectType
from graphql.type import GraphQLInt as Int
from graphql.type import GraphQLList
from graphql.type import GraphQLNonNull
from graphql.type import GraphQLObjectType
from graphql.type import GraphQLString as String
from graphql.type import GraphQLType


from typed_graphql.util import get_arg_for_typevar

from typing_inspect import is_new_type, is_optional_type, is_typevar

if sys.version_info >= (3, 10):
    from types import NoneType, UnionType
else:
    NoneType = type(None)
    UnionType = None

RESERVED_ARGUMENT_NAMES = set(["data", "info", "return"])

IMMUTABLE_ARGUMENT_NAMES = set(["includeDeprecated"])
"""These arguments should not be snakecased"""


class TypedGraphqlMiddlewareManager(MiddlewareManager):
    def get_field_resolver(self, field_resolver):

        def hydrate_field(name: str, value: Any) -> Any:
            annotations = getattr(field_resolver, '__annotations__', {})
            try:
                field_class = annotations[name]
            except KeyError:
                return value
            snake_case_value = {camel_to_snake(k): v for k, v in value.items()}
            return field_class(**snake_case_value)

        def resolve(data, info, **args):
            args = {
                camel_to_snake(k): hydrate_field(camel_to_snake(k), v)
                for k, v in args.items()
                if k not in IMMUTABLE_ARGUMENT_NAMES
            }
            try:
                return getattr(data, f"resolve_{camel_to_snake(info.field_name)}")(
                    info, **args
                )
            except AttributeError:
                try:
                    resolver = getattr(data, f"{camel_to_snake(info.field_name)}")
                    if getattr(resolver, "__is_resolver", None):
                        return resolver(info, **args)
                except AttributeError:
                    pass
                return field_resolver(data, info, **args)

        return resolve


F = TypeVar('F', bound=Callable[..., Any])


def resolver(f: F) -> F:
    """
    This method is a resolver
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    wrapper.__is_resolver = True  # type: ignore
    return cast(F, wrapper)


def staticresolver(f: F) -> F:
    """
    This method is a resolver
    We also automatically decorate it as a staticmethod
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    wrapper.__is_resolver = True  # type: ignore
    return cast(F, staticmethod(wrapper))


def graphql_input_type(cls):
    if hasattr(cls, "_graphql_input_type"):
        return cls._graphql_input_type

    fields = {}

    public_attrs = (
        (attr_name, y)
        for attr_name, y in cls.__annotations__.items()
        if not attr_name.startswith("_")
    )

    for attr_name, attr in public_attrs:
        if attr_name.startswith("_"):
            continue
        field = InputField(python_type_to_graphql_type(cls, attr, input_field=True))
        field_name = snake_to_camel(attr_name, upper=False)
        fields[field_name] = field

    if not cls.__name__.endswith("Input"):
        name = f"{cls.__name__}Input"
    else:
        name = cls.__name__

    cls._graphql_input_type = GraphQLInputObjectType(name, fields)

    return cls._graphql_input_type


class resolverclass:  # NOQA
    def __init__(self, resolver_blocklist: Optional[List[str]] = None):
        self._resolver_blocklist = resolver_blocklist

    def __call__(self, cls):
        cls._resolver_blocklist = self._resolver_blocklist
        return cls


def parse_dataclass_fields(cls) -> Dict[str, Field]:
    fields = {}

    # Obtain docstring
    docstring = cls.__doc__
    parsed_docstring = docstring_parser.parse(docstring)
    arg_name_to_doc = {x.arg_name: x.description for x in parsed_docstring.params}

    for f in dataclass_fields(cls):
        if f.name in (getattr(cls, "_resolver_blocklist", None) or []):
            continue
        field_name = snake_to_camel(f.name, upper=False)

        def resolver(data, info):
            return getattr(data, camel_to_snake(info.field_name), None)

        field = Field(
            python_type_to_graphql_type(cls, f.type),
            resolve=resolver,
            description=arg_name_to_doc.get(f.name),
        )
        fields[field_name] = field

    return fields


def parse_dict_fields(cls) -> Dict[str, Field]:
    fields = {}

    # Obtain docstring
    docstring = cls.__doc__
    parsed_docstring = docstring_parser.parse(docstring)
    arg_name_to_doc = {x.arg_name: x.description for x in parsed_docstring.params}

    annotations = getattr(cls, '__annotations__', {})
    for name, type in annotations.items():
        if name in (getattr(cls, "_resolver_blocklist", None) or []):
            continue
        field_name = snake_to_camel(name, upper=False)

        def resolver(data, info):
            return getitem(data, camel_to_snake(info.field_name))

        field = Field(
            python_type_to_graphql_type(cls, type),
            resolve=resolver,
            description=arg_name_to_doc.get(name),
        )
        fields[field_name] = field

    return fields


def graphql_type(cls, input_field: bool = False) -> GraphQLType:
    """
    Converts a class into a GraphQLType via introspection

    input_field: is this an GraphQL input type?
    """

    if input_field:
        return graphql_input_type(cls)

    # Check cache
    if hasattr(cls, "_graphql_type"):
        return cls._graphql_type

    fields = {}

    def is_staticmethod(o):
        return o.__class__.__name__ == "staticmethod"

    def is_resolver(o):
        if is_staticmethod(o):
            o = o.__func__
        try:
            if o.__name__.startswith("resolve_"):
                return True
        except AttributeError:
            return False
        return getattr(o, "__is_resolver", False)

    def inspect_signature(o):
        if o.__class__.__name__ == "staticmethod":
            return inspect.signature(o.__func__)
        return inspect.signature(o)

    # It's a dataclass so let's auto expose the fields
    # Though an explicit resolver function always takes precedence
    if is_dataclass(cls):
        fields.update(parse_dataclass_fields(cls))

    elif issubclass(cls, dict):
        fields.update(parse_dict_fields(cls))

    resolvers = [
        (attr_name, y)
        for klass in cls.__mro__
        for attr_name, y in klass.__dict__.items()
        if is_resolver(y)
    ]

    for attr_name, attr in resolvers:
        signature = inspect_signature(attr)
        params = list(signature.parameters.items())
        if not params:
            raise Exception("First two args should be 'data' and 'info'")

        arg_offset = 2
        if len(params) < 2:
            raise Exception("First three args should be 'self', and 'info'")

        has_snake_case_args = any(
            "_" in param_name for param_name, param in params[arg_offset:]
        )

        # Obtain docstring
        if is_staticmethod(attr):
            docstring = attr.__func__.__doc__
        else:
            docstring = attr.__doc__

        parsed_docstring = docstring_parser.parse(docstring)
        arg_name_to_doc = {x.arg_name: x.description for x in parsed_docstring.params}

        args = {}

        for param_name, param in params[arg_offset:]:
            try:
                args[snake_to_camel(param_name, upper=False)] = GraphQLArgument(
                    python_type_to_graphql_type(cls, param.annotation, input_field=True),
                    description=arg_name_to_doc.get(param_name, ""),
                    default_value=param.default if param.default != inspect._empty else Undefined,
                )
            except PythonToGraphQLTypeConversionException:
                raise TypeUnrepresentableAsGraphql(
                    f"Type '{param.annotation}' for '{param_name}' of {cls.__name__}.{attr_name} can not be converted to a GraphQL type",
                )

        try:
            return_type = cls.__annotations__[attr_name].__args__[-1]
        except (AttributeError, KeyError):
            return_type = signature.return_annotation
            # return_type = attr.__annotations__["return"]

        # TODO: Need async version
        def resolver_shim(func, data, info, *args, **kwargs):
            kwargs = {camel_to_snake(k): v for k, v in kwargs.items()}
            return func(data, info, *args, **kwargs)

        if is_staticmethod(attr):
            if has_snake_case_args:
                resolver = partial(resolver_shim, attr.__func__)
            else:
                resolver = attr.__func__
        else:
            if has_snake_case_args:
                resolver = partial(resolver_shim, attr)
            else:
                resolver = attr

        try:
            graphql_ret_type = python_type_to_graphql_type(cls, return_type)
        except PythonToGraphQLTypeConversionException:
            raise ReturnTypeMissing(f"{attr_name} of {cls} is missing return type")
        except TypeUnrepresentableAsGraphql as e:
            if e.original_exception:
                # print(inspect.getsource(attr))
                raise TypeUnrepresentableAsGraphql(
                    f"Return type {return_type} for {attr_name} can not be converted to a GraphQL type",
                    e,
                )
            raise

        if is_staticmethod(attr):
            field = Field(graphql_ret_type, args=args, resolve=resolver)
        else:
            field = Field(graphql_ret_type, args=args)

        if attr_name.startswith("resolve_"):
            attr_name = attr_name[len("resolve_") :]

        field_name = snake_to_camel(attr_name, upper=False)
        fields[field_name] = field

    docstring = cls.__doc__
    parsed_docstring = docstring_parser.parse(docstring)

    try:
        graphql_type = GraphQLObjectType(
            cls.__name__, fields, description=parsed_docstring.short_description
        )
    except TypeError as e:
        raise TypeUnrepresentableAsGraphql(cls.__name__, e)

    # Some types are immutable
    try:
        cls._graphql_type = graphql_type
    except TypeError:
        return graphql_type

    return cls._graphql_type


class PythonToGraphQLTypeConversionException(Exception):
    pass


class TypeUnrepresentableAsGraphql(Exception):
    """When a type can't be represented as GraphQL"""

    def __init__(self, name: str, e: Optional[Exception] = None):
        self.name = name
        self.original_exception = e


class ReturnTypeMissing(Exception):
    pass


def is_annotated(cls) -> bool:
    return get_origin(cls) is Annotated


def python_type_to_graphql_type(cls, t, nonnull=True, input_field=False):
    if type(t) is GenericAlias:
        origin = get_origin(t)
        if origin is list or origin is set:
            assert len(t.__args__) == 1
            _t = GraphQLList(python_type_to_graphql_type(cls, t.__args__[0], nonnull=True))
            if nonnull:
                return GraphQLNonNull(_t)
            return _t

    elif UnionType is not None and type(t) is UnionType:
        args = get_args(t)
        if 2 < len(args) or args[1] is not NoneType:
            raise Exception("union that is not equivalent to Optional is not supported")
        return python_type_to_graphql_type(cls, args[0], nonnull=False, input_field=input_field)

    elif str(t).startswith("typing.AsyncIterator"):
        assert len(t.__args__) == 1
        _t = GraphQLList(python_type_to_graphql_type(cls, t.__args__[0], nonnull=True))
        if nonnull:
            return GraphQLNonNull(_t)
        return _t
    elif str(t).startswith("typing.Iterable"):
        assert len(t.__args__) == 1
        _t = GraphQLList(python_type_to_graphql_type(cls, t.__args__[0], nonnull=True))
        if nonnull:
            return GraphQLNonNull(_t)
        return _t
    elif str(t).startswith("typing.Iterator"):
        assert len(t.__args__) == 1
        _t = GraphQLList(python_type_to_graphql_type(cls, t.__args__[0], nonnull=True))
        if nonnull:
            return GraphQLNonNull(_t)
        return _t
    elif str(t).startswith("typing.List"):
        assert len(t.__args__) == 1
        _t = GraphQLList(python_type_to_graphql_type(cls, t.__args__[0], nonnull=True, input_field=input_field))
        if nonnull:
            return GraphQLNonNull(_t)
        return _t
    elif str(t).startswith("typing.Set"):
        assert len(t.__args__) == 1
        _t = GraphQLList(python_type_to_graphql_type(cls, t.__args__[0], nonnull=True, input_field=input_field))
        if nonnull:
            return GraphQLNonNull(_t)
        return _t
    elif str(t).startswith("typing.Tuple"):
        if not len(set(t.__args__)) == 1:
            raise Exception("tuples must have the same type for all members")
        _t = GraphQLList(python_type_to_graphql_type(cls, t.__args__[0], nonnull=True, input_field=input_field))
        if nonnull:
            return GraphQLNonNull(_t)
        return _t
    if str(t).startswith("graphql.type.definition.GraphQLList"):
        assert len(t.__args__) == 1
        return GraphQLList(
            python_type_to_graphql_type(cls, t.__args__[0], nonnull=True)
        )
    elif is_annotated(t):
        # if a GraphQLType is in the annotation, we use that as an override
        for annotated_type in get_args(t):
            try:
                is_graphqltype = issubclass(annotated_type, GraphQLType)
            except TypeError:
                pass
            else:
                if is_graphqltype:
                    return annotated_type()

        # otherwise we try to use the first type
        return python_type_to_graphql_type(cls, get_args(t)[0], nonnull=nonnull, input_field=input_field)

    elif is_optional_type(t):
        if len(t.__args__) == 2:
            if issubclass(t.__args__[1], type(None)):
                return python_type_to_graphql_type(cls, t.__args__[0], nonnull=False, input_field=input_field)
            else:
                raise Exception
        else:
            raise Exception

    elif is_new_type(t):
        return python_type_to_graphql_type(
            cls, t.__supertype__, input_field=input_field, nonnull=nonnull,
        )

    elif is_dataclass(t):
        _t = graphql_type(t, input_field=input_field)
        if nonnull:
            return GraphQLNonNull(_t)
        return _t

    elif isinstance(t, GraphQLObjectType):
        if nonnull:
            return GraphQLNonNull(t)
        return t

    elif is_typevar(t):
        t = get_arg_for_typevar(t, cls)
        return python_type_to_graphql_type(
            cls, t, nonnull=nonnull, input_field=input_field
        )

    else:

        try:
            if issubclass(t, str):
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
            elif issubclass(t, enum.Enum):
                if not hasattr(t, "_graphql_type"):
                    t._graphql_type = GraphQLEnumType(t.__name__, dict(t.__members__))
                if nonnull:
                    return GraphQLNonNull(t._graphql_type)
                return t._graphql_type

            elif issubclass(t, dict):
                if nonnull:
                    return GraphQLNonNull(graphql_type(t, input_field=input_field))
                return graphql_type(t, input_field=input_field)

            elif issubclass(t, inspect._empty):
                raise PythonToGraphQLTypeConversionException(t)

            # A simple class
            elif issubclass(t, object):
                if nonnull:
                    return GraphQLNonNull(graphql_type(t, input_field=input_field))
                return graphql_type(t, input_field=input_field)

            else:
                raise PythonToGraphQLTypeConversionException(t)

        except TypeError:
            print(f"Bad type: {t} of {type(t)}")
            raise
