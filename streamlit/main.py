import streamlit as st
import httpx

from app.database.database import Chat

client = httpx.Client(base_url="http://localhost:8000")

st.title("Chat App")


if "chats" not in st.session_state:
    chats = client.get("/chats").json()
    chats = [Chat.model_validate(chat) for chat in chats]
    st.session_state.chats = {chat.id: chat for chat in chats}
    st.session_state.chat = None
    st.session_state.history = []


def select_chat(chat_id=None):
    if chat_id is not None:
        st.session_state.chat = st.session_state.chats[chat_id]
        history = client.get(f"/chats/{chat_id}/messages").json()
        for message in history:
            if message["role"] == "ai":
                message["role"] = "assistant"
        st.session_state.history = history
    else:
        st.session_state.chat = None
        st.session_state.history = []
    return


with st.sidebar:
    for chat in st.session_state.chats.values():
        st.button(
            chat.title,
            use_container_width=True,
            on_click=select_chat,
            kwargs={"chat_id": chat.id},
        )


CSS = """\
<style>
.stChatMessage:has([data-testid="stChatMessageAvatarUser"]) {
    display: flex;
    flex-direction: row-reverse;
    align-itmes: end;
    text-align: left;
}
</style>
"""

st.html(CSS)

if st.session_state.history is not None:
    for message in st.session_state.history:
        # Display chat messages from history on app rerun
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
        stream = streaming(st.session_state.chat.id, prompt)
        response = st.write_stream(stream)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
