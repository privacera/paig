import os
import random
from unittest.mock import patch

import pytest

from paig_common.audit_spooler import AuditSpooler, AuditEvent
from paig_common.file_utils import FileUtils
from paig_common.paig_exception import DiskFullException


class TestAuditEvent:

    def __init__(self, **kwargs):
        self.event_time = kwargs.get("event_time")

    def to_payload_dict(self):
        request_dict = {
            "eventTime": self.event_time
        }

        return request_dict

    @classmethod
    def from_payload_dict(cls, payload_dict):
        kwargs = {
            "event_time": payload_dict.get("eventTime")
        }
        return cls(**kwargs)


@pytest.fixture(scope="module")
def temp_directory(tmpdir_factory):
    return tmpdir_factory.mktemp("test_data")


def test_get_spooled_audit_events(temp_directory):
    # Create a temporary directory for spooling
    audit_spool_dir = str(temp_directory.join("spool"))

    # Create an instance of AuditSpooler
    spooler = AuditSpooler(audit_spool_dir=audit_spool_dir, audit_event_cls=TestAuditEvent)

    # Create some temporary audit event files
    file1 = audit_spool_dir + "/audit_spool_2022-01-01.json"
    FileUtils.append_json_to_file(file1, {"eventTime": 1640995200000})

    file1 = audit_spool_dir + "/audit_spool_2022-01-02.json"
    FileUtils.append_json_to_file(file1, {"eventTime": 1641081600000})

    # Call the method being tested
    audit_events = spooler.get_spooled_audit_events()

    # Check the result
    assert len(audit_events) == 2


def test_add_audit_event(temp_directory):
    # Create a temporary directory for spooling
    audit_spool_dir = str(temp_directory.join("spool" + str(random.randint(0, 1000))))

    # Create an instance of AuditSpooler
    spooler = AuditSpooler(audit_spool_dir=audit_spool_dir, audit_event_cls=TestAuditEvent)

    # Create a mock audit event
    event_time = 1640995200000  # January 1, 2022
    test_event = TestAuditEvent.from_payload_dict({"eventTime": event_time})

    # Call the method being tested
    spooler.add_audit_event(test_event)

    # Check if the audit event file is created
    expected_file_path = os.path.join(audit_spool_dir, "audit_spool_2022-01-01.json")

    # Read the content of the audit event file and check if the event is present
    data = spooler.get_spooled_audit_events()
    assert len(data) == 1
    assert data[0].event_time == 1640995200000


def test_remove_audit_event(temp_directory):
    # Create a temporary directory for spooling
    audit_spool_dir = str(temp_directory.join("spool_test_remove_audit_event_" + str(random.randint(0, 1000))))

    # Create an instance of AuditSpooler
    spooler = AuditSpooler(audit_spool_dir=audit_spool_dir, audit_event_cls=TestAuditEvent)

    # Create a mock audit event
    event_time = 1640995200000  # January 1, 2022
    test_event = TestAuditEvent.from_payload_dict({"eventTime": event_time})

    # Add the mock event to the spooler
    spooler.add_audit_event(test_event)

    # Call the method being tested
    spooler.remove_audit_event(test_event)

    # Check if the audit event file is removed
    files_present = FileUtils.get_file_paths_in_directory(audit_spool_dir)
    assert len(files_present) == 0


def test_get_file_path_for_event_time(temp_directory):
    # Create a temporary directory for spooling
    audit_spool_dir = str(temp_directory.join("spool"))

    # Create an instance of AuditSpooler
    spooler = AuditSpooler(audit_spool_dir=audit_spool_dir, audit_event_cls=TestAuditEvent)

    # Define an event time in milliseconds
    event_time_millis = 1640995200000  # January 1, 2022

    # Call the method being tested
    file_path = spooler.get_file_path_for_event_time(event_time_millis)

    # Check if the file path is generated correctly
    expected_file_path = os.path.join(audit_spool_dir, "audit_spool_2022-01-01.json")
    assert file_path == expected_file_path


class MockAuditEvent(AuditEvent):
    def to_payload_dict(self):
        return {"eventTime": 1640995200000}

    @classmethod
    def from_payload_dict(cls, payload_dict):
        return cls()


@patch('paig_common.audit_spooler.FileUtils.append_json_to_file')
@patch('paig_common.audit_spooler.AuditSpooler.get_file_path_for_event_time')
def test_add_audit_event_exception(mock_get_file_path_for_event_time, mock_append_json_to_file, temp_directory):
    # Create a temporary directory for spooling
    audit_spool_dir = str(temp_directory.join("spool"))
    mock_get_file_path_for_event_time.return_value = audit_spool_dir
    mock_append_json_to_file.side_effect = OSError(28, "No space left on device. Disk is full. Please increase the "
                                                       "disk size or free"
                                                       "up some space to push audits successfully.")
    spooler = AuditSpooler(audit_spool_dir, MockAuditEvent)

    with pytest.raises(DiskFullException) as e:
        spooler.add_audit_event(MockAuditEvent())
    assert str(e.value) == ("No space left on device. Disk is full. Please increase the disk size or free up some "
                            "space to push audits successfully.")
