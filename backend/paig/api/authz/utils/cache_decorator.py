import time
from functools import wraps
from typing import Callable, Any

# Global cache and timestamp dictionaries
cache = {}
cache_last_called = {}


def make_hashable(obj: Any) -> Any:
    """Convert non-hashable types to hashable ones."""
    if isinstance(obj, (list, set, tuple)):
        return tuple(make_hashable(e) for e in obj)
    if isinstance(obj, dict):
        return tuple((k, make_hashable(v)) for k, v in sorted(obj.items()))
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    raise TypeError(f"Unhashable type: {type(obj)}")


def cache_with_expiration(expiration: int):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract the class name and function name
            class_name = args[0].__class__.__name__
            function_name = func.__name__

            # Create a unique key using the FQDN and argument values
            fqdn = f"{class_name}.{function_name}"
            key = (fqdn, make_hashable(args[1:]), make_hashable(kwargs))

            # Check if the result is already cached and if it is not expired
            if key not in cache or time.time() - cache_last_called.get(key, 0) > expiration:
                # Call the actual function and store the result in the cache
                cache[key] = await func(*args, **kwargs)
                cache_last_called[key] = time.time()

            return cache[key]

        return wrapper

    return decorator
