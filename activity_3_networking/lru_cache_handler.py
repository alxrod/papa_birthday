# cache_handler.py

from collections import OrderedDict
import time

# Set a small cache size (adjust as needed)
MAX_CACHE_SIZE = 2  # This will store only 2 items at a time

# Use OrderedDict to implement LRU cache
cache = OrderedDict()

def check_cache(filename):
    """
    Check if a file is in the cache.
    Returns the file content if it's in the cache, None otherwise.
    """
    if filename in cache:
        # Move the accessed item to the end (most recently used)
        cache.move_to_end(filename)
        print(f"Cache hit for {filename}")
        return cache[filename]
    print(f"Cache miss for {filename}")
    return None

def update_cache(filename, content):
    """
    Update the cache with new content.
    Implements LRU eviction if cache is full.
    """
    if filename in cache:
        # If file already in cache, move it to the end and update content
        cache.move_to_end(filename)
    elif len(cache) >= MAX_CACHE_SIZE:
        # If cache is full, remove the least recently used item (first item)
        cache.popitem(last=False)
    
    # Add new item to the cache
    cache[filename] = content
    print(f"Updated cache with {filename}")

def print_cache_stats():
    """
    Print cache statistics.
    """
    print("\nCache Statistics:")
    print(f"Current cache size: {len(cache)}")
    print(f"Cache contents: {list(cache.keys())}")