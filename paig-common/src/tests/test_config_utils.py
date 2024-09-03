from unittest import mock
from io import BytesIO
from jproperties import Properties

from paig_common import config_utils


# Mock logger
@mock.patch('paig_common.config_utils.logger')
def test_load_config_file(mock_logger):
    # Mock open to simulate reading a config file
    with mock.patch('builtins.open', mock.mock_open(read_data=b'key1=value1\nkey2=value2')):
        config_utils.load_config_file('dummy_path')
        assert config_utils.configs_properties.get('key1').data == 'value1'
        assert config_utils.configs_properties.get('key2').data == 'value2'
        mock_logger.info.assert_called_with('Loading config file dummy_path')


def test_get_property_value():
    # Prepare properties
    props = Properties()
    props.load(BytesIO(b'key1=value1\nkey2=value2'))
    config_utils.configs_properties = props

    # Test existing and non-existing keys
    assert config_utils.get_property_value('key1') == 'value1'
    assert config_utils.get_property_value('key2') == 'value2'
    assert config_utils.get_property_value('key3', 'default') == 'default'
    assert config_utils.get_property_value('key3') is None


def test_get_property_value_int():
    props = Properties()
    props.load(BytesIO(b'key1=1\nkey2=not_an_int'))
    config_utils.configs_properties = props

    assert config_utils.get_property_value_int('key1') == 1
    assert config_utils.get_property_value_int('key2') is None
    assert config_utils.get_property_value_int('key2', 42) == 42
    assert config_utils.get_property_value_int('key3', 42) == 42


def test_get_property_value_float():
    props = Properties()
    props.load(BytesIO(b'key1=1.5\nkey2=not_a_float'))
    config_utils.configs_properties = props

    assert config_utils.get_property_value_float('key1') == 1.5
    assert config_utils.get_property_value_float('key2') is None
    assert config_utils.get_property_value_float('key2', 42.0) == 42.0
    assert config_utils.get_property_value_float('key3', 42.0) == 42.0


def test_get_property_value_boolean():
    props = Properties()
    props.load(BytesIO(b'key1=true\nkey2=false\nkey3=not_a_boolean'))
    config_utils.configs_properties = props

    assert config_utils.get_property_value_boolean('key1') is True
    assert config_utils.get_property_value_boolean('key2') is False
    assert config_utils.get_property_value_boolean('key3') is False
    assert config_utils.get_property_value_boolean('key3', True) is False
    assert config_utils.get_property_value_boolean('key4', False) is False


def test_get_keys():
    props = Properties()
    props.load(BytesIO(b'key1=value1\nkey2=value2'))
    config_utils.configs_properties = props

    keys = config_utils.get_keys()
    assert 'key1' in keys
    assert 'key2' in keys
    assert 'key3' not in keys


def test_get_property_value_list():
    # Prepare properties
    props = Properties()
    props.load(BytesIO(b'key1=value1,value2,value3\nkey2=value4'))
    config_utils.configs_properties = props

    # Test existing and non-existing keys
    assert config_utils.get_property_value_list('key1') == ['value1', 'value2', 'value3']
    assert config_utils.get_property_value_list('key2') == ['value4']
    assert config_utils.get_property_value_list('key3', 'default') == ['default']
    assert config_utils.get_property_value_list('key3') is None
