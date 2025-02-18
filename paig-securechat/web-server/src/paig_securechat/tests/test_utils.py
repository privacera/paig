import os
import uuid
import pytest
from unittest.mock import patch
from unittest.mock import mock_open

from core.utils import (
    get_uuid, generate_title, extract_keywords, summarize_conversation,
    construct_title, recursive_merge_dicts, set_paig_api_key
)


def test_get_uuid():
    uuid_value = get_uuid()
    assert isinstance(uuid_value, str)
    assert len(uuid_value) == 32



def test_generate_title():
    conversation = ["Hello, how are you?", "I'm good, thanks!", "Let's talk about Python."]
    title = generate_title(conversation)
    assert isinstance(title, str)
    assert "Python" in title  # Ensuring the main topic appears


def test_extract_keywords():
    conversation = ["Hello world", "Hello Python"]
    keywords = extract_keywords(conversation)
    assert isinstance(keywords, set)
    assert "Hello" in keywords
    assert "Python" in keywords
    assert "world" in keywords


def test_summarize_conversation():
    conversation = ["Message 1", "Message 2", "Message 3", "Message 4"]
    summary = summarize_conversation(conversation)
    assert summary == "Message 2 Message 3 Message 4"


def test_construct_title():
    title = construct_title("Python", {"code", "learning"}, "Python is great!")
    assert isinstance(title, str)
    assert "Python" in title
    assert "Python is great" in title


def test_recursive_merge_dicts():
    dict1 = {"a": 1, "b": {"x": 10}}
    dict2 = {"b": {"y": 20}, "c": 3}
    merged = recursive_merge_dicts(dict1, dict2)
    assert merged == {"a": 1, "b": {"x": 10, "y": 20}, "c": 3}



def test_set_paig_api_key():
    with patch("os.environ", {}), patch("os.path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data="test-paig-api-key")), \
         patch("core.config.Config", {"paig": {"key_file": "test_paig.key"}}):
        set_paig_api_key()
        assert os.environ["PAIG_API_KEY"] == "test-paig-api-key"
        # unset the environment variable
        del os.environ["PAIG_API_KEY"]
