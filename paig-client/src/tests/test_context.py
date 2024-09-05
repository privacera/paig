import threading
import time

import paig_client.client
from unittest.mock import patch


# Define a test function to set the current user_name in a thread-local context
def set_user_in_context(user):
    print(f"Setting user_name {user} in context")
    paig_client.client.set_current_user(user)
    for i in range(10):
        time.sleep(0.1)
        current_user = paig_client.client.get_current_user()
        print(
            f"thread ident={threading.get_ident()}, thread native_id= {threading.get_native_id()} - Current user_name in context: {current_user}")
        assert current_user == user
    paig_client.client.clear()


# Test setting and clearing user_name context in a multithreading environment
def test_user_context_threads(setup_paig_plugin_with_app_config_file_name):
    with patch("paig_client.backend.ShieldRestHttpClient.init_shield_server", return_value=None):
        paig_client.client.setup(application_config_file=setup_paig_plugin_with_app_config_file_name, frameworks=["langchain"])
        thread_list = []
        for i in range(10):
            this_thread = threading.Thread(target=set_user_in_context, args=[f"test_user_{i}"])
            this_thread.start()
            thread_list.append(this_thread)

        for this_thread in thread_list:
            this_thread.join()
