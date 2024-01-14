from diskcache import Cache
from functools import wraps

# Create a global cache object
import pandas as pd
report_date = pd.Timestamp('today').strftime('%F')
cache = Cache(f'./{report_date}')

def cache_control(expire=None):
    """
    A decorator that adds caching with control to any function. It allows
    the function to either use the cache, refresh the cache, or bypass it.

    Parameters:
    - expire (int): The time in seconds until the cache expires. Defaults to 60 seconds.

    The decorated function gains two additional keyword arguments:
    - use_cache (bool): If True (default), the function will attempt to use cached values.
    - refresh_cache (bool): If True, the cache for the specific call is refreshed. This argument
      overrides `use_cache` if both are True.

    Returns:
    - A wrapped function with caching capabilities.
    """
    def decorator(func):
        # Wrap the function with memoize
        memoized_func = cache.memoize(expire=expire)(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            use_cache = kwargs.pop('use_cache', True)
            refresh_cache = kwargs.pop('refresh_cache', False)

            key = memoized_func.__cache_key__(*args, **kwargs)

            if refresh_cache:
                # Invalidate and refresh the cache
                cache.delete(key)
                result = func(*args, **kwargs)
                cache.set(key, result, expire=expire)
                return result
            elif use_cache:
                try:
                    # Use the memoized function (with caching)
                    return cache[key]
                except KeyError:
                    result = func(*args, **kwargs)
                    cache[key] = result
                    return result
            else:
                # Bypass cache and call the original function
                return func(*args, **kwargs)

        return wrapper
    return decorator

@cache_control(expire=60)
def my_function(*args, **kwargs):
    # Function logic here
    return ...  # Replace with the actual return statement

# Example Usage
a = 1
b = 2
result = my_function(a, b, use_cache=True)  # Tries to load from cache
print(result)

result = my_function(a, b, refresh_cache=True)  # Refreshes/overrides cache
print(result)

result = my_function(a, b, use_cache=False)  # Runs the function without caching
print(result)
