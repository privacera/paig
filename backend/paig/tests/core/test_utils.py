from core.utils import get_password_hash, verify_password, recursive_merge_dicts


def test_recursive_merge_dicts():
    dict1 = {
            "key1": "value1",
            "key2": "value2"
        }
    dict2 = {
            "key2": "value3",
            "key3": "value4"
        }

    result = recursive_merge_dicts(dict1, dict2)
    assert result == {
            "key1": "value1",
            "key2": "value3",
            "key3": "value4"
        }


def test_verify_password():
    password = "valid_password"
    hashed_password = get_password_hash(password)
    assert verify_password(password, hashed_password)
    assert not verify_password("wrong_password", hashed_password)
    assert not verify_password("", hashed_password)


def test_get_password_hash():
    password = "valid_password"
    hashed_password = get_password_hash(password)
    assert hashed_password != password
    assert len(hashed_password) > 0
