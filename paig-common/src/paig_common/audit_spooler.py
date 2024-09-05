import abc
import json
import logging
import os
import queue
import threading
import time
from abc import ABC, abstractmethod
from datetime import datetime, date
from queue import Queue
from typing import List, TypeVar

from .file_utils import FileUtils
from .paig_exception import AuditEventQueueFullException, DiskFullException

_logger = logging.getLogger(__name__)
T = TypeVar('T')


class AuditEvent(ABC):

    def __init__(self, **kwargs):
        """
        Initializes a AuditEvent object.

        Keyword Arguments:
            event_time (str): The timestamp of the event.
        """

        self.event_time = kwargs.get("event_time")

    @abstractmethod
    def to_payload_dict(self):
        """
        Returns a dictionary representation of the AuditEvent object.

        Returns:
            dict: A dictionary containing the attributes of the event.
        """
        pass

    @classmethod
    @abstractmethod
    def from_payload_dict(cls, payload_dict):
        """
        Creates a AuditEvent object from a dictionary payload.

        Args:
            payload_dict (dict): Dictionary containing attributes of the event.

        Returns:
            AuditEvent: An instance of AuditEvent.
        """
        pass


class AuditSpooler:
    """
    Class to manage spooled audit events.

    Args:
        audit_spool_dir (str): The directory path where spooled audit events are stored.
    """

    def __init__(self, audit_spool_dir: str, audit_event_cls):
        """
        Initializes an AuditSpooler object.

        Args:
            audit_spool_dir (str): The directory path where spooled audit events are stored.
        """
        self.audit_spool_dir = audit_spool_dir
        self.audit_event_cls = audit_event_cls

        if not os.path.exists(self.audit_spool_dir):
            os.makedirs(self.audit_spool_dir)

        self.lock = threading.Lock()

    def get_spooled_audit_events(self):
        """
        Retrieves spooled audit events from the spool directory.

        Returns:
            List[AuditEvent]: A list of AuditEvent objects representing spooled audit events.
        """
        spooled_audit_events = []

        file_paths = FileUtils.get_file_paths_in_directory(self.audit_spool_dir)
        for file_path in file_paths:
            with self.lock:
                spooled_events = FileUtils.load_json_from_file(file_path)
                for event_dict_str in spooled_events:
                    event_dict = json.loads(event_dict_str)
                    access_audit_event = self.audit_event_cls.from_payload_dict(event_dict)
                    spooled_audit_events.append(access_audit_event)

        return spooled_audit_events

    def add_audit_event(self, access_audit_event: T):
        """
        Adds an audit event to the spool directory.

        Args:
            access_audit_event (AuditEvent): The audit event to add.
        """
        event_time = self.get_event_time(access_audit_event)
        file_path = self.get_file_path_for_event_time(event_time)
        access_audit_event_dict = access_audit_event.to_payload_dict()
        try:
            with self.lock:
                FileUtils.append_json_to_file(file_path, access_audit_event_dict)
        except OSError as e:
            if e.errno == 28:
                _logger.error("No space left on device. Disk is full.Please increase the disk size or free "
                              "up some space to push audits successfully.")
                raise DiskFullException("No space left on device. Disk is full. Please increase the disk size or free "
                                        "up some space to push audits successfully.")
            else:
                _logger.error(f"Error writing audit event to file: {e}")
                raise Exception(f"Error writing audit event to file: {e}")

    def get_event_time(self, access_audit_event):
        event_time = None
        if hasattr(access_audit_event, 'event_time'):
            event_time = access_audit_event.event_time
        elif hasattr(access_audit_event, 'eventTime'):
            event_time = access_audit_event.eventTime
        return event_time

    def remove_audit_event(self, access_audit_event: T):
        """
        Removes an audit event from the spool directory.

        Args:
            access_audit_event (AuditEvent): The audit event to remove.
        """
        event_time = self.get_event_time(access_audit_event)
        file_path = self.get_file_path_for_event_time(event_time)
        access_audit_event_dict = access_audit_event.to_payload_dict()
        with self.lock:
            FileUtils.remove_line_from_file(file_path, access_audit_event_dict)

        today = date.today()
        today_file_name = today.strftime("audit_spool_%Y-%m-%d.json")

        # Call remove_empty_files method with today's file name in the exclude list
        exclude_files = [today_file_name]
        FileUtils.remove_empty_files(self.audit_spool_dir, exclude_files)

    def get_file_path_for_event_time(self, event_time_millis) -> str:
        """
        Generates the file path for the given event time.

        Args:
            event_time_millis (int): The event time in milliseconds.

        Returns:
            str: The file path for the given event time.
        """
        event_date = datetime.fromtimestamp(event_time_millis / 1000)  # Convert milliseconds to seconds
        return os.path.join(self.audit_spool_dir, f"audit_spool_{event_date.strftime('%Y-%m-%d')}.json")


class AuditLogger(threading.Thread, metaclass=abc.ABCMeta):
    """
    A class to log audit data and push it to a server.

    Attributes:
        audit_spool_dir (str): A directory to store spooled audit files.
    """

    def __init__(self, audit_spool_dir: str, audit_event_cls, max_queue_size=10000, audit_event_queue_timeout=5):
        """
        Initializes the AuditLogger.

        Args:
            audit_spool_dir (str): Audit spool directory
            audit_event_cls (cls): Class of audit event
        """
        super().__init__()

        self.audit_event_queue_timeout = audit_event_queue_timeout
        self.audit_spooler = AuditSpooler(audit_spool_dir, audit_event_cls)

        self.audit_event_queue = Queue(maxsize=max_queue_size)
        self.failed_audit_event_queue = Queue(maxsize=max_queue_size)

        # Load spooled audits
        self.load_spooled_audit_events()

        self.retry_failed_audit_thread = threading.Thread(target=self.retry_failed_audit_events)
        self.retry_failed_audit_thread.daemon = True  # Daemonize the thread
        self.retry_failed_audit_thread.start()

    def retry_failed_audit_events(self):
        """
        Periodically retries failed audit events from the failed audit event queue.

        This method continuously retrieves failed audit events from the failed audit event queue,
        adds them back to the audit event queue for retry, and waits for 2 minutes before retrying
        again. The retry process ensures that failed audit events are reprocessed at regular intervals.

        """
        while True:
            failed_audit_events = []
            while not self.failed_audit_event_queue.empty():
                failed_audit_event = self.failed_audit_event_queue.get()
                failed_audit_events.append(failed_audit_event)

            if failed_audit_events:
                _logger.debug(f"Retrying {len(failed_audit_events)} failed audit events.")
                for failed_audit_event in failed_audit_events:
                    self.audit_event_queue.put(failed_audit_event, timeout=self.audit_event_queue_timeout)
            else:
                _logger.debug("No failed audit events to retry.")

            # Wait for 2 minutes and try this failed audit retries every 2 mins interval
            time.sleep(120)

    def load_spooled_audit_events(self):
        """
        Loads spooled audit events from the AuditSpooler and puts them into the audit event queue.

        This method retrieves spooled audit events from the AuditSpooler and puts them into the audit event queue for processing.

        """
        spooled_audit_events = self.audit_spooler.get_spooled_audit_events()
        for audit_event in spooled_audit_events:
            self.audit_event_queue.put(audit_event, timeout=self.audit_event_queue_timeout)

    def log(self, audit_event: T):
        """
        Logs the provided data.

        Args:
            audit_event (object): The audit event to be logged.
        """
        # Add event to spool file
        self.audit_spooler.add_audit_event(audit_event)
        try:
            self.audit_event_queue.put(audit_event, timeout=self.audit_event_queue_timeout)
        except queue.Full:
            _logger.error("Audit event queue is full.The push rate is too high for the audit spooler to process.")
            raise AuditEventQueueFullException("Audit event queue is full.The push rate is too high for the audit "
                                               "spooler to process.")

    def run(self):
        """
        Runs the AuditLogger thread.

        Continuously checks for new events in the audit_event_queue and pushes them to the server.
        """
        try:
            while True:
                # Check for new logs in the audit_event_queue
                # This is a blocking queue, it will implicitly wait till record available in queue
                audit_event = self.audit_event_queue.get()
                try:
                    # Push audit to server
                    self.push_audit_event_to_server(audit_event)
                    if _logger.isEnabledFor(logging.DEBUG):
                        _logger.debug("Audit event data pushed to server: %s", audit_event)

                    # After successfully pushing audits to server, removing it from spool directory
                    self.audit_spooler.remove_audit_event(audit_event)
                except Exception as e:
                    _logger.warning("Failed to push audit event data %s to server: %s. Retrying request. Will add it "
                                    "back in the audit-queue.", audit_event, e)
                    # Adding failed audits for retries
                    self.failed_audit_event_queue.put(audit_event, timeout=self.audit_event_queue_timeout)
        except Exception as e:
            _logger.error("An error occurred in AuditLogger: %s", e)

    @abstractmethod
    def push_audit_event_to_server(self, audit_event: T):
        """
        Abstract method to push an audit event to the server.

        Subclasses must implement this method to define how audit events are pushed to the server.

        Args:
            audit_event (T): The audit event to be pushed to the server.
                The type of the audit event is specified by the generic type parameter T.

        Raises:
            NotImplementedError: If the method is not implemented by the subclass.
        """
        pass
