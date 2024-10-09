import uuid
from . import constants
import os


def get_uuid() -> str:
    return uuid.uuid4().hex


def generate_title(conversation):
    main_topic = conversation[-1] # Assuming the last user message represents the current topic.
    keywords = extract_keywords(conversation)
    conversation_summary = summarize_conversation(conversation)
    title = construct_title(main_topic, keywords, conversation_summary)
    return title


def extract_keywords(conversation):
    # You can implement your own logic here to extract keywords.
    # This could involve tokenization, removing stop words, and counting word frequency.
    # For simplicity, let's assume keywords are the unique words in the conversation.
    words = ' '.join(conversation).split()
    keywords = set(words)
    return keywords


def summarize_conversation(conversation):
    # You can implement your own logic here to summarize the conversation.
    # For simplicity, let's assume the summary is the last few sentences of the conversation.
    summary = ' '.join(conversation[-3:])  # Assuming the last 3 sentences as the summary.
    return summary


def construct_title(main_topic, keywords, conversation_summary):
    # Step 5: Generate the title based on the identified components.
    # You can implement your own logic here to construct the title.
    # This is a basic example; you can make it more sophisticated.
    title = f"{main_topic} - {conversation_summary[:30]}"  # Combine main topic and a snippet of the summary.
    return title


def recursive_merge_dicts(dict1, dict2):
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = recursive_merge_dicts(result[key], value)
        else:
            result[key] = value

    return result


def set_up_standalone_mode(
        ROOT_DIR,
        debug,
        config_path,
        custom_config_path,
        disable_paig_shield_plugin,
        host,
        port,
        openai_api_key,
        single_user_mode=False
):
    if config_path is None:
        config_path = os.path.join(ROOT_DIR, "configs")
    if custom_config_path is None:
        custom_config_path = 'custom-configs'
    if openai_api_key is not None:
        os.environ["OPENAI_API_KEY"] = str(openai_api_key)

    os.environ["EXT_CONFIG_PATH"] = custom_config_path
    os.environ["SECURE_CHAT_DEPLOYMENT"] = "standalone"
    os.environ["DEBUG"] = str(debug)
    os.environ["CONFIG_PATH"] = str(config_path)
    os.environ["DISABLE_PAIG_SHIELD_PLUGIN"] = str(disable_paig_shield_plugin)
    os.environ["SECURECHAT_ROOT_DIR"] = ROOT_DIR
    constants.HOST = host
    constants.PORT = port
    constants.ROOT_DIR = ROOT_DIR
    constants.MODE = "standalone"
    constants.SINGLE_USER_MODE = single_user_mode

