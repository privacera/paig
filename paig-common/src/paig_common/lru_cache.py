import time
from abc import abstractmethod
from collections import OrderedDict
from datetime import datetime, timedelta
from threading import Lock, Thread
import threading


class LRUCacheEvictCallback:
    """
    A callback to be called when an item is evicted from the cache.
    """

    @abstractmethod
    def __call__(self, key, value):
        """
        Call the callback function.

        Args:
            key (str): The key of the item to be evicted.
            value (Any): The value of the item to be evicted.

        Returns:
            None
        """
        raise NotImplementedError


class LRUCache:
    """
    An implementation of a Least Recently Used (LRU) Cache.

    Args:
        capacity (int): The maximum number of items the cache can hold.
        max_idle_time (int): The maximum time (in seconds) an item can remain idle in the cache.
        cleanup_interval_sec (int): The interval (in seconds) to call cache clearing check.

    Attributes:
        cache (OrderedDict): An ordered dictionary to store key-value pairs, maintaining insertion order.
        capacity (int): The maximum capacity of the cache.
        max_idle_time (int): The maximum idle time (in seconds) allowed for cache items.
        last_access (Dict[str, datetime]): A dictionary to store the last access time of each cache item.
        lock (Lock): A threading lock to ensure thread safety.
        cleanup_interval_sec (int): The interval (in seconds) at which the cache cleanup is performed.
        cleanup_thread (Thread): A background thread for periodic cache cleanup.
        hits (int): The number of cache hits.
        misses (int): The number of cache misses.
        evictions (int): The number of cache evictions.
    """

    def __init__(self, cache_name, capacity, max_idle_time, cleanup_interval_sec, evict_callback: LRUCacheEvictCallback | None = None):
        self.cache = OrderedDict()
        self.capacity = capacity
        self.max_idle_time = max_idle_time
        self.last_access = {}
        self.lock = Lock()
        self.cleanup_interval_sec = cleanup_interval_sec
        self.stop_cleanup_thread_event = threading.Event()
        self.cleanup_thread = Thread(target=self.cleanup_idle_instance, name=f'{cache_name}-cleanup-thread')
        self.cleanup_thread.daemon = True
        self.cleanup_thread.start()
        self.cache_name = cache_name
        self.evict_callback = evict_callback

        # Metrics
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def stop_cleanup_thread(self):
        """
        Stop the cache cleanup thread.

        Returns:
            None
        """
        self.stop_cleanup_thread_event.set()

    def get(self, key):
        """
        Retrieve a value from the cache by key.

        Args:
            key (str): The key to retrieve the value for.

        Returns:
            Any: The value associated with the key, or None if the key is not found.
        """
        with self.lock:
            if key in self.cache:
                value = self.cache.pop(key)
                self.cache[key] = value
                self.last_access[key] = datetime.now()
                self.hits += 1
                return value
            else:
                self.misses += 1
                return None

    def put(self, key, value):
        """
        Put a key-value pair into the cache.

        Args:
            key (str): The key of the item to be stored.
            value (Any): The value to be stored.

        Returns:
            None
        """
        with self.lock:
            if key in self.cache:
                # Remove the old entry and re-insert it to update its position
                self.cache.pop(key)
            elif len(self.cache) >= self.capacity:
                # Evict the least recently used item (the first item in OrderedDict)
                oldest_key, oldest_value = self.cache.popitem(last=False)
                if self.evict_callback:
                    self.evict_callback(oldest_key, oldest_value)
                self.last_access.pop(oldest_key)
                self.evictions += 1

            # Insert the new key-value pair
            self.cache[key] = value
            self.last_access[key] = datetime.now()

    def remove(self, key):
        """
        Remove an item from the cache by key.

        Args:
            key (str): The key of the item to be removed.

        Returns:
            None
        """
        with self.lock:
            if key in self.cache:
                if self.evict_callback:
                    self.evict_callback(key, self.cache[key])
                self.cache.pop(key)
                self.last_access.pop(key)
                self.evictions += 1

    def keys(self):
        """
        Get the keys of the cache.

        Returns:
            List[str]: The list of keys in the cache.
        """
        with self.lock:
            return list(self.cache.keys())

    def cleanup_idle_instance(self):
        """
        Clean up idle cache items periodically.

        Returns:
            None
        """
        while not self.stop_cleanup_thread_event.is_set():
            current_time = datetime.now()
            keys_to_delete = [key for key, last_access_time in self.last_access.items()
                              if (current_time - last_access_time) > timedelta(seconds=self.max_idle_time)]
            for key in keys_to_delete:
                self.remove(key)

            time.sleep(self.cleanup_interval_sec)
