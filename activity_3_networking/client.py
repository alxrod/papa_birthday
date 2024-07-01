import requests
import os
import time
import random
from lru_cache_handler import check_cache, update_cache, print_cache_stats

# Base URL of the slow server
BASE_URL = "http://localhost:8000"
# Directory to store cached files
CACHE_DIR = "cache"

def ensure_cache_dir():
    """Ensure the cache directory exists."""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

def fetch_from_server(filename):
    """
    Request a file from the server and save it locally.
    Returns the file content and the time taken.
    """
    start_time = time.time()
    
    url = f"{BASE_URL}/image/{filename}"
    response = requests.get(url)
    
    if response.status_code == 200:
        content = response.content
        end_time = time.time()
        return content, end_time - start_time
    else:
        end_time = time.time()
        return None, end_time - start_time

def request_file(filename):
    """
    Wrapper function to request a file.
    Checks cache first, then fetches from server if necessary.
    """
    # Check if file is in cache
    cached_content = check_cache(filename)
    if cached_content is not None:
        return cached_content, 0  # Assume cache retrieval is instantaneous
    
    # If not in cache, fetch from server
    content, duration = fetch_from_server(filename)
    if content is not None:
        # Update cache with new content
        update_cache(filename, content)
        
        # Save file locally
        ensure_cache_dir()
        local_path = os.path.join(CACHE_DIR, filename)
        with open(local_path, 'wb') as f:
            f.write(content)
    
    return content, duration

# Example usage
def runTest():
    test_files = ["cardiff.png", "comet.png", "mutiny.png", "macmillian.png"]
    
    # Create a list of 50 file requests with repetitions
    file_requests = random.choices(test_files, k=50)
    
    total_time = 0
    for i, file in enumerate(file_requests, 1):
        content, duration = request_file(file)
        total_time += duration
        if content is not None:
            print(f"Request {i}: File {file} retrieved successfully")
            print(f"Time taken: {duration:.2f} seconds")
        else:
            print(f"Request {i}: Failed to retrieve {file}")
        print("-" * 30)
    
    print(f"Total time taken for all requests: {total_time:.2f} seconds")
    print_cache_stats()