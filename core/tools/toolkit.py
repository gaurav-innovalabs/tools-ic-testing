import inspect
from collections.abc import Callable
from functools import wraps
from typing import Any, ClassVar, TypeVar

from docstring_parser import parse
from pydantic import BaseModel

# Type variables for better type hints
T = TypeVar("T", bound="Toolkit")
F = TypeVar("F", bound=Callable[..., Any])


def _get_json_type_for_py_type(arg: str) -> str:
    """
    Get the JSON schema type for a given type.
    :param arg: The type to get the JSON schema type for.
    :return: The JSON schema type.
    """
    # App.logger.info(f"Getting JSON type for: {arg}")
    if arg in ("int", "float", "complex", "Decimal"):
        return "number"
    if arg in ("str", "string"):
        return "string"
    if arg in ("bool", "boolean"):
        return "boolean"
    if arg in ("NoneType", "None"):
        return "null"
    if arg in ("list", "tuple", "set", "frozenset"):
        return "array"
    if arg in ("dict", "mapping"):
        return "object"

    # If the type is not recognized, return "object"
    return "unknown"


class Toolkit:
    """
    Toolkit class for managing tools and their configurations.

    This class serves to manage and register tools along with their specific
    configurations. Tools can be registered globally, and their functions or
    properties can be accessed using appropriate methods. The Toolkit maintains
    a dictionary of registered tools and their configurations, allowing for
    structured and organized storage.

    Attributes:
        __tools (ClassVar[dict[str, dict[str, Any]]]): A dictionary containing
            all globally registered tools and their associated configurations.
    """

    __tools: ClassVar[dict[str, dict[str, Any]]] = {}

    def __init__(self, configuration: dict[str, Any]):
        self.configuration: dict[str, Any] = (
            configuration if configuration else {"config": {}, "functions": {}, "enable": []}
        )

    @classmethod
    def tool(cls, _cls: str, _func: str = None):
        """Get the tool class name"""
        if _func is None:
            return cls.__tools[_cls]
        return cls.__tools[_cls]["functions"][_func]

    @classmethod
    def register(cls, name: str, kwargs: dict, tool_cls: str = None):
        """Register a tool with its configuration"""
        if tool_cls is not None:
            if tool_cls not in cls.__tools:
                raise ValueError(f"Tool {tool_cls} is not registered")

            d = cls.__tools[tool_cls]
            if name in d["functions"]:
                raise ValueError(f"Tool {name} is already registered in {tool_cls}")
            d["functions"][name] = kwargs
        else:
            cls.__tools[name] = kwargs


def tool(
    schema: type[BaseModel] | None = None,
    title: str = None,
    description: str = None,
    icon: str = None,
    category: str = None,
):
    """
    Defines a decorator function `tool` that registers a class with specific metadata
    attributes such as title, icon, category, schema, and other configuration details.
    The `tool` function is designed to be used as a higher-order function for
    enhanced customization of the annotated class.

    Parameters:
        title (str, optional): A short display name for the tool. Defaults to None.
        icon (str, optional): A string representing an icon associated with the tool. Defaults to None.
        category (str, optional): Specifies the category of the tool for organization purposes. Defaults to None.
        schema (type[BaseModel] | None, optional): A Pydantic BaseModel-derived schema
        used to describe the JSON structure for the tool's representation. Defaults to None.

    Returns:
        Callable[[type[T]], type[T]]: A decorator function that takes a class, registers its
        metadata, and returns the class unchanged.

    Raises:
        None
    """

    def decorator(cls: type[T]) -> type[T]:
        kwargs = {
            "id": cls.__name__,
            "title": title,
            "description": description or cls.__doc__,
            "icon": icon,
            "category": category,
            "functions": {},
            "schema": schema.model_json_schema() if schema else None,
        }
        Toolkit.register(cls.__name__, kwargs)
        return cls

    return decorator


def tool_func(schema: type[BaseModel] | None = None, title: str = None, desc: str = None):
    """
    Decorator to register a function as a tool in a toolkit with additional metadata.

    This decorator is designed to enhance a function by attaching metadata such as
    an optional ID, schema, and other configurations. It registers the function within
    a toolkit, making it identifiable and customizable while maintaining function
    behavior.

    Parameters
    ----------
    title : str, optional
        A title for the tool, default is None.
    desc : str, optional
        A description of the tool, default is None.
    schema : type[BaseModel] or None, optional
        A Pydantic model representing the schema for the tool, default is None.

    Returns
    -------
    Callable
        A decorated function that registers the tool with the toolkit and adds
        configuration management.
    """

    def decorator(func: F) -> F:
        parsed = parse(inspect.getdoc(func))
        sig = inspect.signature(func)
        args = []
        for name, param in sig.parameters.items():
            if name == "self" or name == "_config":
                continue
            args.append(
                {
                    "name": name,
                    "description": next((p.description for p in parsed.params if p.arg_name == name), ""),
                    "optional": param.default is not inspect.Parameter.empty,
                    "default": param.default if param.default is not inspect.Parameter.empty else None,
                    "type": _get_json_type_for_py_type(
                        param.annotation.__name__ if param.annotation is not inspect.Parameter.empty else "any"
                    ),
                }
            )

        kwargs = {
            "id": func.__name__,
            "title": title,
            "description": desc,
            "parameters": {},
            "returns": {"type": ",", "description": ""},
            "schema": schema.model_json_schema() if schema else None,
            "enabled": True,
            "llm_tool": {},
        }
        tool_cls = func.__qualname__.split(".")[0]
        # if tool_cls not in Toolkit.__tools:# temp fix tool_func run 1st , lastly run @tool -> regester issue
        #     Toolkit.__tools[tool_cls] = kwargs 
        Toolkit.register(func.__name__, kwargs, tool_cls=tool_cls)

        @wraps(func)
        def wrapper(self: any, *args, **kwargs) -> any:
            kwargs["_config"] = self.configuration.get("functions", {"config": ""}).get("config", {})
            return func(self, *args, **kwargs)

        return wrapper

    return decorator
