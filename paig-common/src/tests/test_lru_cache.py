import time
from threading import Thread

import pytest
from unittest.mock import Mock
from paig_common.lru_cache import LRUCache, LRUCacheEvictCallback


@pytest.fixture
def cache():
    return LRUCache("test-cache", 5, 5, 1)  # Create a cache with capacity 5 and max idle time 5 seconds


def test_put_and_get(cache):
    cache.put("key1", "value1")
    assert cache.get("key1") == "value1"  # Check if the value is retrieved correctly


def test_cache_eviction(cache):
    for i in range(5):
        cache.put(f"key{i}", f"value{i}")
    for i in range(4, -1, -1):
        cache.get(f"key{i}")
    cache.put("key6", "value6")
    assert cache.get("key4") is None  # Check if key0 has been evicted


def test_cache_cleanup(cache):
    cache.put("key1", "value1")
    cache.put("key2", "value2")
    time.sleep(6)
    assert cache.get("key1") is None


def test_cache_stop_cleanup(cache):
    cache.put("key1", "value1")
    cache.put("key2", "value2")
    cache.stop_cleanup_thread()
    time.sleep(6)
    assert cache.get("key1") == "value1"


def test_cache_hits_and_misses(cache):
    cache.put("key1", "value1")
    assert cache.get("key1") == "value1"  # Cache hit
    assert cache.get("key2") is None  # Cache miss
    assert cache.hits == 1
    assert cache.misses == 1


def test_cache_capacity_handling(cache):
    for i in range(5):
        cache.put(f"key{i}", f"value{i}")
    cache.put("key5", "value5")  # This should cause the first inserted key to be evicted
    assert len(cache.keys()) == 5  # Ensure cache size is within capacity
    assert cache.get("key0") is None  # Ensure the oldest item was evicted


def test_eviction_callback(cache):
    mock_callback = Mock(spec=LRUCacheEvictCallback)
    cache_with_callback = LRUCache("test-cache-cb", 2, 5, 1, evict_callback=mock_callback)
    cache_with_callback.put("key1", "value1")
    cache_with_callback.put("key2", "value2")
    cache_with_callback.put("key3", "value3")  # This should trigger eviction of key1

    mock_callback.assert_called_once_with("key1", "value1")


def test_thread_safety(cache):
    def put_items():
        for i in range(50):
            cache.put(f"key{i}", f"value{i}")

    def get_items():
        for i in range(50):
            cache.get(f"key{i}")

    threads = [Thread(target=put_items), Thread(target=get_items)]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    # Ensure the cache size doesn't exceed the capacity and no exceptions were raised
    assert len(cache.keys()) <= cache.capacity


def test_manual_removal_of_items(cache):
    cache.put("key1", "value1")
    cache.put("key2", "value2")
    cache.remove("key1")
    assert cache.get("key1") is None
    assert cache.get("key2") == "value2"
    assert "key1" not in cache.keys()
