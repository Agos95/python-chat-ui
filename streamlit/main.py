# from http_client import client
import httpx
from uuid import uuid4

import streamlit as st
from app.database import database as db


@st.cache_resource
def get_httpx_client():
    return httpx.Client(base_url="http://localhost:8000")


client = get_httpx_client()


def get_chats():
    chats = client.get("/chats").json()
    chats = [db.Chat.model_validate(chat) for chat in chats]
    st.session_state.chats = {chat.id: chat for chat in chats}


def select_chat(chat_id=None):
    if chat_id is not None:
        st.session_state.chat = st.session_state.chats[chat_id]
        history = client.get(f"/chats/{chat_id}/messages").json()
        st.session_state.history = [db.ChatMessage.model_validate(h) for h in history]
    else:
        st.session_state.chat = None
        st.session_state.history = None
    return


def render_chat():
    chat = st.session_state.chat is not None
    if chat is None:
        return
    title.title(f"{st.session_state.chat.title}")
    if st.session_state.history is not None:
        message: db.ChatMessage
        for message in st.session_state.history:
            render_message(message)


def delete_chat(chat_id: str):
    client.delete(f"chats/{chat_id}")
    select_chat(st.session_state.chat.id)


def render_message(message: db.ChatMessage):
    # Display chat messages from history on app rerun
    role = message.role
    col_message, col_delete = st.columns([0.975, 0.025], vertical_alignment="bottom")
    with col_message:
        with st.chat_message(role):
            st.markdown(message.content)
    with col_delete:
        st.button(
            "",
            help="Delete",
            on_click=delete_message,
            kwargs={"message_id": message.id},
            icon=":material/delete:",
            key=f"delete_{message.id}_{uuid4().hex}",
            use_container_width=True,
            type="tertiary",
        )


def delete_message(message_id: str):
    client.delete(f"messages/{message_id}")
    select_chat(st.session_state.chat.id)


# STREAMLIT

title = st.title("Chat App")


if "chats" not in st.session_state:
    get_chats()
    st.session_state.chat = None
    st.session_state.history = None


with st.sidebar:
    for chat in st.session_state.chats.values():
        col_title, col_delete = st.columns([0.9, 0.1])
        with col_title:
            st.button(
                chat.title,
                type="secondary",
                use_container_width=True,
                on_click=select_chat,
                kwargs={"chat_id": chat.id},
            )
        with col_delete:
            st.button(
                "",
                help="Delete",
                on_click=delete_chat,
                kwargs={"message_id": chat.id},
                icon=":material/delete:",
                key=f"delete_{chat.id}",
                use_container_width=True,
                type="tertiary",
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

# st.html(CSS)

is_chat_selected = st.session_state.chat is not None


if is_chat_selected:
    render_chat()
    prompt = st.chat_input()

else:
    prompt = st.chat_input("Select a chat", disabled=True)


def streaming(chat_id: str, message: str):
    with client.stream(
        "POST",
        f"/chats/{chat_id}/stream",
        json={"content": message},
    ) as r:
        for chunk in r.iter_text():
            yield chunk


# React to user input
if prompt:
    placeholder = st.empty()
    with placeholder.container():
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Response
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            with st.spinner(text=""):
                stream = streaming(st.session_state.chat.id, prompt)
                response = st.write_stream(stream)
    placeholder.empty()
    select_chat(st.session_state.chat.id)
    for message in st.session_state.history[-2:]:
        render_message(message)
