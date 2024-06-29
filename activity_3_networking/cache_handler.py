# cache_handler.py
from collections import OrderedDict

cache = {}

def check_cache(filename):
    """
    Check if a file is in the cache.
    Returns the file content if it's in the cache, None otherwise.
    """
    # TODO: Implement cache checking logic
    return None

def update_cache(filename, content):
    """
    Update the cache with new content.
    """
    # TODO: Implement cache updating logic
    pass

def print_cache_stats():
    """
    Print cache statistics.
    """
    print("\nCache Statistics:")
    print(f"Current cache size: {len(cache)}")
    print(f"Cache contents: {list(cache.keys())}")