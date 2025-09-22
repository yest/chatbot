# Import the necessary libraries
import streamlit as st  # For creating the web app interface
from google import genai  # For interacting with the Google Gemini API

# --- 1. Page Configuration and Title ---

# Set the title and a caption for the web page
st.title("Guru Matematika Virtual")
st.caption("Guru matematika virtual yang membantu anda memahami konsep matematika dengan jelas dan mudah.")

# --- 2. Sidebar for Settings ---

# Create a sidebar section for app settings using 'with st.sidebar:'
with st.sidebar:
    # Add a subheader to organize the settings
    st.subheader("Settings")
    
    # Create a text input field for the Google AI API Key.
    # 'type="password"' hides the key as the user types it.
    google_api_key = st.text_input("Google AI API Key", type="password")
    
    # Create a button to reset the conversation.
    # 'help' provides a tooltip that appears when hovering over the button.
    reset_button = st.button("Reset Conversation", help="Clear all messages and start fresh")

# --- 3. API Key and Client Initialization ---

# Check if the user has provided an API key.
# If not, display an informational message and stop the app from running further.
if not google_api_key:
    st.info("Masukkan Google AI API Key untuk melanjutkan.", icon="🗝️")
    st.stop()

# This block of code handles the creation of the Gemini API client.
# It's designed to be efficient: it only creates a new client if one doesn't exist
# or if the user has changed the API key in the sidebar.

# We use `st.session_state` which is Streamlit's way of "remembering" variables
# between user interactions (like sending a message or clicking a button).

# Condition 1: "genai_client" not in st.session_state
# Checks if we have *never* created the client before.
#
# Condition 2: getattr(st.session_state, "_last_key", None) != google_api_key
# This is a safe way to check if the current API key is different from the last one we used.
# `getattr(object, 'attribute_name', default_value)` tries to get an attribute from an object.
# If the attribute doesn't exist, it returns the default value (in this case, `None`).
# So, it checks: "Is the key stored in memory different from the one in the input box?"
if ("genai_client" not in st.session_state) or (getattr(st.session_state, "_last_key", None) != google_api_key):
    try:
        # If the conditions are met, create a new client.
        st.session_state.genai_client = genai.Client(api_key=google_api_key)
        # Store the new key in session state to compare against later.
        st.session_state._last_key = google_api_key
        # Since the key changed, we must clear the old chat and message history.
        # .pop() safely removes an item from session_state.
        st.session_state.pop("chat", None)
        st.session_state.pop("messages", None)
    except Exception as e:
        # If the key is invalid, show an error and stop.
        st.error(f"Invalid API Key: {e}")
        st.stop()


# --- 4. Chat History Management ---

# Initialize the chat session if it doesn't already exist in memory.
if "chat" not in st.session_state:
    # Create a new chat instance using the 'gemini-2.5-flash' model.
    st.session_state.chat = st.session_state.genai_client.chats.create(model="gemini-2.5-flash")

# Initialize the message history (as a list) if it doesn't exist.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Handle the reset button click.
if reset_button:
    # If the reset button is clicked, clear the chat object and message history from memory.
    st.session_state.pop("chat", None)
    st.session_state.pop("messages", None)
    # st.rerun() tells Streamlit to refresh the page from the top.
    st.rerun()

# --- 5. Display Past Messages ---

# Loop through every message currently stored in the session state.
for msg in st.session_state.messages:
    # For each message, create a chat message bubble with the appropriate role ("user" or "assistant").
    with st.chat_message(msg["role"]):
        # Display the content of the message using Markdown for nice formatting.
        st.markdown(msg["content"])

# --- 6. Handle User Input and API Communication ---

# Create a chat input box at the bottom of the page.
# The user's typed message will be stored in the 'prompt' variable.
prompt = st.chat_input("Type your message here...")

# Definisikan sistem prompt agar chatbot bertindak sebagai guru matematika dalam bahasa Indonesia.
system_prompt = (
    "Anda adalah seorang guru matematika yang ramah dan berpengetahuan luas. "
    "Jelaskan konsep dengan jelas, berikan solusi langkah demi langkah, dan dorong siswa untuk belajar. "
    "Jika siswa bertanya tentang matematika, bimbing mereka dengan sabar dan gunakan contoh jika memungkinkan. "
    "Selalu gunakan bahasa Indonesia yang mudah dipahami."
)

# Check if the user has entered a message.
if prompt:
    # 1. Add the user's message to our message history list.
    st.session_state.messages.append({"role": "user", "content": prompt})
    # 2. Display the user's message on the screen immediately for a responsive feel.
    with st.chat_message("user"):
        st.markdown(prompt)

    # 3. Get the assistant's response.
    try:
        # Send the user's prompt to the Gemini API, prepending the system prompt.
        # Combine the system prompt and conversation history for context.
        conversation = [
            {"role": "system", "content": system_prompt}
        ] + st.session_state.messages

        # Concatenate messages for the Gemini API.
        # If the API supports a list of messages, use it; otherwise, join as a single string.
        conversation_text = "\n".join(
            f"{msg['role'].capitalize()}: {msg['content']}" for msg in conversation
        )

        response = st.session_state.chat.send_message(conversation_text)

        if hasattr(response, "text"):
            answer = response.text
        else:
            answer = str(response)

    except Exception as e:
        answer = f"An error occurred: {e}"

    # 4. Display the assistant's response.
    with st.chat_message("assistant"):
        st.markdown(answer)
    # 5. Add the assistant's response to the message history list.
    st.session_state.messages.append({"role": "assistant", "content": answer})