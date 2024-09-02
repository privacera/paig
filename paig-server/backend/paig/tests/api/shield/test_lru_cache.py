import time

import pytest
from api.shield.cache.lru_cache import LRUCache


@pytest.fixture
def cache(mocker):
    side_effect = lambda prop, default_value=None: {
        "cache_cleanup_interval_sec": 1
    }.get(prop, default_value)

    mocker.patch('api.shield.utils.config_utils.get_property_value_int', side_effect=side_effect)
    return LRUCache("test-cache", 5, 5)  # Create a cache with capacity 5 and max idle time 5 seconds


def test_put_and_get(cache):
    cache.put("key1", "value1")
    assert cache.get("key1") == "value1"  # Check if the value is retrieved correctly


def test_cache_eviction(cache):
    # Fill up the cache
    for i in range(5):
        cache.put(f"key{i}", f"value{i}")

    # Access the keys in reverse order, making key4 the least recently used
    for i in range(4, -1, -1):
        cache.get(f"key{i}")

    # Add a new key-value pair, causing key0 to be evicted
    cache.put("key6", "value6")
    assert cache.get("key4") is None  # Check if key0 has been evicted


def test_cache_cleanup(cache):
    # Add some key-value pairs
    cache.put("key1", "value1")
    cache.put("key2", "value2")

    time.sleep(6)  # Wait for max_idle_time
    assert cache.get("key1") is None  # Check if key1 has been evicted
