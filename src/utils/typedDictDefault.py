import types
from typing import Any, TypeVar, Union, cast, get_args, get_origin, get_type_hints


class DefaultTypeError(TypeError):
    """Exception raised when default value cannot be created for a type."""

    def __init__(self, field_name: str, field_type: type):
        super().__init__(
            f"Failed to create default value for field '{field_name}' "
            f"with type {field_type}. Add support for this type in _get_default_value()"
        )
        self.field_name = field_name
        self.field_type = field_type


def _get_default_value(field_type: type, field_name: str = "<unknown>") -> Any:
    """
    Recursively creates a default value for the given type.

    Args:
        field_type: The type of the field
        field_name: Name of the field (for informative errors)

    Returns:
        Default value for the given type

    Raises:
        DefaultTypeError: If the type is not supported
    """
    origin = get_origin(field_type)

    # Base types
    if field_type is str:
        return ""
    elif field_type is int:
        return 0
    elif field_type is float:
        return 0.0
    elif field_type is bool:
        return False
    elif field_type is bytes:
        return b""
    elif field_type is type(None):
        return None

    # Collections
    elif origin is list:
        return []
    elif origin is dict:
        return {}
    elif origin is set:
        return cast(set[Any], set())
    elif origin is tuple:
        # For tuple, check elements
        args = get_args(field_type)
        if args:
            return tuple(
                _get_default_value(arg, f"{field_name}[{i}]")
                for i, arg in enumerate(args)
            )
        return ()

    # Optional/Union types - extract helper to avoid duplication
    elif origin in (types.UnionType, Union):
        return _handle_union_type(field_type, field_name)

    # Unknown type
    else:
        raise DefaultTypeError(field_name, field_type)


def _handle_union_type(field_type: type, field_name: str) -> Any:
    """
    Handle Union/Optional types by trying each non-None variant.

    Args:
        field_type: The Union type
        field_name: Name of the field for error messages

    Returns:
        Default value from the first successful non-None type, or None
    """
    args = get_args(field_type)
    for arg in args:
        if arg is not type(None):
            try:
                return _get_default_value(arg, field_name)
            except DefaultTypeError:
                continue
    return None


T = TypeVar("T")


def create_default(typed_dict_class: type[T]) -> T:
    """
    Creates an object with default values for any TypedDict.
    Analog of Rust's Default trait with recursive support for nested structures.

    Args:
        typed_dict_class: The TypedDict class

    Returns:
        Dictionary with default values for all fields

    Raises:
        DefaultTypeError: If a field has an unsupported type
    """
    hints = get_type_hints(typed_dict_class)
    result: dict[str, Any] = {}

    for field_name, field_type in hints.items():
        try:
            result[field_name] = _get_default_value(field_type, field_name)
        except DefaultTypeError as e:
            # Rethrow with parent class context
            raise DefaultTypeError(
                f"{typed_dict_class.__name__}.{e.field_name}", e.field_type
            ) from e

    return result  # type: ignore[return-value]
