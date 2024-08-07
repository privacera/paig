from unittest.mock import patch

from api.shield.presidio.nlp_handler import NLPHandler


@patch('os.path.exists')
def test_get_nlp_engine_with_custom_conf_file(mock_exists):
    # Mocking the existence of the custom config file
    mock_exists.return_value = True

    # Create two instances of NLPHandler
    handler1 = NLPHandler()
    handler2 = NLPHandler()

    # Get the NLP engine from both instances
    engine1 = handler1.get_engine()
    engine2 = handler2.get_engine()

    # Check if the engines returned are the same object
    assert engine1 is engine2


@patch('os.path.exists')
def test_get_nlp_engine_with_default_conf_file(mock_exists):
    # Mocking the existence of the custom config file
    mock_exists.return_value = False

    # Create two instances of NLPHandler
    handler1 = NLPHandler()
    handler2 = NLPHandler()

    # Get the NLP engine from both instances
    engine1 = handler1.get_engine()
    engine2 = handler2.get_engine()

    # Check if the engines returned are the same object
    assert engine1 is engine2
