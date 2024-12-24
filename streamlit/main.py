import streamlit as st
import httpx

from app.database.database import Chat

client = httpx.Client(base_url="http://localhost:8000")

st.title("Chat App")


if "chats" not in st.session_state:
    chats = client.get("/chats").json()
    st.session_state.chats = [Chat.model_validate(chat) for chat in chats]

with st.sidebar:
    for chat in st.session_state.chats:
        st.button(chat.title, key=chat.id, use_container_width=True)


CSS = """\
<style>
.stChatMessage:has([data-testid="stChatMessageAvatarUser"]) {
    display: flex;
    flex-direction: row-reverse;
    align-itmes: end;
    text-align: right;
}
</style>
"""

st.html(CSS)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
prompt = st.chat_input("How can I help you?")
if prompt:
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})


def streaming(chat_id: str, message: str):
    with httpx.Client() as client:
        with client.stream(
            "POST",
            f"http://localhost:8000/chats/{chat_id}",
            json={"message": message},
        ) as r:
            for chunk in r.iter_text():
                yield chunk


# Response
if prompt:
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        stream = streaming("gwerage", prompt)
        response = st.write_stream(stream)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
