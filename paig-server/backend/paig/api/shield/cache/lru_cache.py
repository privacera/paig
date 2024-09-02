import time
import logging
from collections import OrderedDict
from datetime import datetime, timedelta
from threading import Lock, Thread

from api.shield.utils import config_utils
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.metrics import Observation

# TODO - Add this in otel module
# Initialize the meter provider
metrics.set_meter_provider(MeterProvider())
meter = metrics.get_meter(__name__)

logger = logging.getLogger(__name__)


class LRUCache:
    """
    An implementation of a Least Recently Used (LRU) Cache.

    Args:
        capacity (int): The maximum number of items the cache can hold.
        max_idle_time (int): The maximum time (in seconds) an item can remain idle in the cache.

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

    def __init__(self, cache_name, capacity, max_idle_time):
        self.cache = OrderedDict()
        self.capacity = capacity
        self.max_idle_time = max_idle_time
        self.last_access = {}
        self.lock = Lock()
        self.cleanup_interval_sec = config_utils.get_property_value_int("cache_cleanup_interval_sec",
                                                                        120)
        self.cleanup_thread = Thread(target=self.cleanup_idle_instance)
        self.cleanup_thread.daemon = True
        self.cleanup_thread.start()
        self.cache_name = cache_name

        # Metrics
        self.hits = 0
        self.misses = 0
        self.evictions = 0

        # OTel metrics
        self.cache_size_metric = meter.create_observable_gauge(
            name=self.cache_name + "_cache_size",
            callbacks=[self.get_cache_size],
            description="The current size of the cache"
        )

        self.cache_hit_ratio_metric = meter.create_observable_gauge(
            name=self.cache_name + "cache_hit_ratio",
            callbacks=[self.get_cache_hit_ratio],
            description="The cache hit ratio"
        )

        self.cache_eviction_rate_metric = meter.create_observable_gauge(
            name=self.cache_name + "cache_eviction_rate",
            callbacks=[self.get_cache_eviction_rate],
            description="The cache eviction rate"
        )

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
                self.cache.pop(key)
            elif len(self.cache) >= self.capacity:
                oldest_key, _ = self.cache.popitem(last=False)
                self.last_access.pop(oldest_key)
                self.evictions += 1
            self.cache[key] = value
            self.last_access[key] = datetime.now()

    def cleanup_idle_instance(self):
        """
        Clean up idle cache items periodically.

        Returns:
            None
        """
        while True:
            with self.lock:
                current_time = datetime.now()
                keys_to_delete = [key for key, last_access_time in self.last_access.items()
                                  if (current_time - last_access_time) > timedelta(seconds=self.max_idle_time)]
                for key in keys_to_delete:
                    self.cache.pop(key)
                    self.last_access.pop(key)
                    self.evictions += 1
                    logger.info(f"Evicted key: {key} from cache: {self.cache_name}")

            time.sleep(self.cleanup_interval_sec)

    def get_cache_size(self, options):
        """
        Get the current size of the cache.

        Returns:
            Iterable[Observation]: The current number of items in the cache.
        """
        with self.lock:
            return [Observation(value=len(self.cache))]

    def get_cache_hit_ratio(self, options):
        """
        Get the cache hit ratio.

        Returns:
            Iterable[Observation]: The cache hit ratio.
        """
        with self.lock:
            total_accesses = self.hits + self.misses
            if total_accesses == 0:
                return [Observation(value=0.0)]
            return [Observation(value=self.hits / total_accesses)]

    def get_cache_eviction_rate(self, options):
        """
        Get the cache eviction rate.

        Returns:
            Iterable[Observation]: The cache eviction rate.
        """
        with self.lock:
            total_accesses = self.hits + self.misses
            if total_accesses == 0:
                return [Observation(value=0.0)]
            return [Observation(value=self.evictions / total_accesses)]
