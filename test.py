import json
from functools import wraps

# Global registry
TOOL_REGISTRY = {}

# Temporary function storage (so function decorators work before class decorator)
PENDING_FUNCTIONS = {}

def register_tool(cls):
    """Registers the class in TOOL_REGISTRY after all methods are decorated."""
    class_name = cls.__name__
    TOOL_REGISTRY[class_name] = {
        "title": getattr(cls, "title", class_name),
        "description": getattr(cls, "description", ""),
        "icon": getattr(cls, "icon", ""),
        "category": getattr(cls, "category", ""),
        "functions": PENDING_FUNCTIONS.pop(class_name, [])  # Attach functions if any
    }
    return cls  # Return class unchanged

def register_tool_func(config_cls, title):
    """Decorator to register tool functions under the respective class."""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, *args, **kwargs)

        # Extract class name from function's __qualname__
        class_name = func.__qualname__.split(".")[0]

        # Store function details in PENDING_FUNCTIONS (will be added after class registers)
        PENDING_FUNCTIONS.setdefault(class_name, []).append({
            "name": func.__name__,
            "title": title,
            "config_class": config_cls.__name__ if hasattr(config_cls, "__name__") else str(config_cls),
            "doc": func.__doc__
        })

        return wrapper
    return decorator

# -------------------------------
# Example Usage
# -------------------------------

@register_tool
class SerpApiTool:
    title = "SerpApi Tools"
    description = "Tools for interacting with SerpApi"
    icon = "serpapi"
    category = "Search"

    def __init__(self, api_key):
        self.api_key = api_key

    @register_tool_func(config_cls=dict, title="Search Google")
    def search_google(self, query: str, _config: dict):
        """
        Performs a Google search and returns results.
        """
        return {"query": query, "status": "success"}

# Print the registry
print(json.dumps(TOOL_REGISTRY, indent=2))
