from paig_client import client as paig_shield_client
from paig_client.model import ConversationType
import paig_client.exception
import uuid
from openai import OpenAI
import streamlit as st

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[View the source code](https://github.com/rivanjuthani/paig/tree/main/examples/streamlit)"
    "[View the PAIG documentation](https://docs.paig.ai/index.html)"

st.title("💬 Chatbot Demo using PAIG")
st.caption("🚀 A Streamlit chatbot powered by OpenAI using PAIG Client")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

if "thread_id" not in st.session_state:
    # Generate a random UUID which will be used to bind a prompt with a reply
    st.session_state["thread_id"] = str(uuid.uuid4())

if "initialized" not in st.session_state:
    # Initialize PAIG Shield Client if not done before
    paig_shield_client.setup(frameworks=[])
    st.session_state["initialized"] = True

# Replace "streamlit_user" with the user who is using the application. Or you can use the service username
user = "streamlit_user"

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    # Create OpenAI client with API key
    client = OpenAI(api_key=openai_api_key)

    try:
        with paig_shield_client.create_shield_context(username=user):
            print(f"User Prompt: {prompt}")
            # Validate prompt with Privacera Shield
            updated_prompt_text = paig_shield_client.check_access(
                text=prompt,
                conversation_type=ConversationType.PROMPT,
                thread_id=st.session_state["thread_id"]
            )
            updated_prompt_text = updated_prompt_text[0].response_text
            print(f"User Prompt (After Privacera Shield): {updated_prompt_text}")
            if prompt != updated_prompt_text:
                print(f"Updated prompt text: {updated_prompt_text}")

            # Add updated prompt to chat history & display it in UI
            st.session_state.messages.append({"role": "user", "content": updated_prompt_text})
            st.chat_message("user").write(updated_prompt_text)

            # Get response from LLM using updated prompt
            response = client.chat.completions.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
            llm_response = response.choices[0].message.content
            print(f"LLM Response: {llm_response}")

            # Validate LLM response with Privacera Shield
            updated_reply_text = paig_shield_client.check_access(
                text=llm_response,
                conversation_type=ConversationType.REPLY,
                thread_id=st.session_state["thread_id"]
            )

            updated_reply_text = updated_reply_text[0].response_text
            print(f"LLM Response (After Privacera Shield): {updated_reply_text}")

            st.session_state.messages.append({"role": "assistant", "content": updated_reply_text})
            st.chat_message("assistant").write(updated_reply_text)
    except paig_client.exception.AccessControlException as e:
        # If access is denied, then this exception will be thrown. You can handle it accordingly.
        print(f"AccessControlException: {e}")