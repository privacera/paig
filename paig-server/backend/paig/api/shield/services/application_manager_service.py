import logging

from api.shield.scanners.scanner_util import parse_properties
from api.shield.cache.lru_cache import LRUCache
from api.shield.utils import config_utils
import concurrent.futures

from api.shield.utils.custom_exceptions import ShieldException
import time

from core.utils import Singleton

logger = logging.getLogger(__name__)


class ApplicationManager(Singleton):
    """
    The ApplicationManager class is responsible for managing the application's scanners.
    It uses an LRUCache to store the scanners for each application key.
    """
    def __init__(self):
        """
        Initialize the ApplicationManager with a cache of scanners.
        The cache's capacity and idle time are configurable.
        """
        if self.is_instance_initialized():
            return
        max_capacity = config_utils.get_property_value_int("max_scanners_cache_capacity", 100)
        max_idle_time = config_utils.get_property_value_int("max_scanners_cache_idle_time", 1800)
        self.cache_name = "ApplicationKey_Scanners"
        self.application_key_scanners = LRUCache(self.cache_name, max_capacity, max_idle_time)
        self.shield_scanner_max_workers = config_utils.get_property_value_int("shield_scanner_max_workers", 4)

    def load_scanners(self, application_key):
        """
        Load the scanners for the given application key and store them in the cache.

        Args:
            application_key (str): The application key.
        """
        scanner_list = parse_properties(application_key)
        self.application_key_scanners.put(application_key, scanner_list)
        logger.info(f"Found {scanner_list} scanners for application key: {application_key}")

    def get_scanners(self, application_key):
        """
        Get the scanners for the given application key.
        If the scanners are not in the cache, load them.

        Args:
            application_key (str): The application key.

        Returns:
            list: The list of scanners for the application key.
        """
        if application_key not in self.application_key_scanners.cache:
            self.load_scanners(application_key)
        return self.application_key_scanners.get(application_key)

    def scan_messages(self, application_key, message):
        """
        Scan the given messages for all the scanners where the enforce access control flag is true.

        Args:
            application_key (str): The application key.
            message (str): The message to scan.

        Returns:
            tuple: A tuple containing the scan results and the access control results.
        """

        scanners = self.get_scanners(application_key)
        logger.debug(f"Found {len(scanners)} scanners for application key: {application_key}")

        scan_results = {}
        scan_timings = {}
        access_control_traits = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.shield_scanner_max_workers) as executor:
            future_to_scanner = {executor.submit(scan_with_scanner, scanner, message): scanner for scanner in scanners}
            for future in concurrent.futures.as_completed(future_to_scanner):
                scanner = future_to_scanner[future]
                try:
                    scanner_name, result, message_scan_time = future.result()
                    scan_results[scanner_name] = result
                    scan_timings[scanner_name] = message_scan_time
                    if scanner.enforce_access_control:
                        access_control_traits.extend(result.get("traits", []))
                except Exception as e:
                    logger.error(f"Scanner {scanner.name} failed with exception: {e}")
                    raise ShieldException(f"Scanner {scanner.name} failed with exception: {e}")
        return scan_results, access_control_traits, scan_timings


def scan_with_scanner(scanner, message):
    """
    Scan the given message with the given scanner.

    Args:
        scanner (Scanner): The scanner to use.
        message (str): The message to scan.

    Returns:
        dict: The scan results.
    """
    logger.debug(f"Scanning message with scanner: {scanner.name}")
    message_scan_start_time = time.perf_counter()
    result = scanner.scan(message)
    logger.debug(f"Scanner {scanner.name} got this result: {result} for message: {message}, which is having access "
                 f"control: {scanner.enforce_access_control}")
    message_scan_time = f"{((time.perf_counter() - message_scan_start_time) * 1000):.3f}"
    return scanner.name, result, message_scan_time
