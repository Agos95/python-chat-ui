from uuid import uuid4

import httpx
import schema

import streamlit as st
from app.database import database as db
from settings import backend_settings, ui_settings


@st.cache_resource
def get_httpx_client():
    return httpx.Client(base_url=backend_settings.BASE_URL, timeout=600)


client = get_httpx_client()


@st.dialog("Edit Chat Title")
def set_title(chat_id: str):
    """Set chat title"""
    if title := st.text_input("New Title"):
        client.patch(f"/chats/{chat_id}", json={"title": title}).json()
        get_chats()
        if st.session_state.chat.id == chat_id:
            select_chat(chat_id)
        st.rerun()


def create_chat() -> None:
    """Create new chat"""
    response = client.post("/chats").json()
    chat = db.Chat.model_validate(response)
    st.session_state.chats = {chat.id: chat} | st.session_state.chats
    select_chat(chat.id)
    return


def get_chats() -> None:
    """Get chats from db and store in streamlit session state"""
    chats = client.get("/chats").json()
    chats = [db.Chat.model_validate(chat) for chat in chats]
    st.session_state.chats = {chat.id: chat for chat in chats}
    return


def select_chat(chat_id=None) -> None:
    """Update streamlit session state with selected chat details"""
    if chat_id is not None:
        st.session_state.chat = st.session_state.chats[chat_id]
        history = client.get(f"/chats/{chat_id}/messages").json()
        st.session_state.history = [
            db.ChatMessage.model_validate(h) for h in history[::-1]
        ]
        st.session_state.title = (
            st.session_state.chat.title or ui_settings.DEFAULT_CHAT_TITLE
        )
    else:
        st.session_state.chat = None
        st.session_state.history = None
        st.session_state.title = ui_settings.APP_TITLE
    return


def render_chat() -> None:
    """Render the selected chat in streamlit session state"""
    chat = st.session_state.chat is not None
    if chat is None:
        return
    if st.session_state.history is not None:
        message: db.ChatMessage
        for message in st.session_state.history:
            render_message(message)
    return


def delete_chat(chat_id: str) -> None:
    """Delete the chat from db and refresh streamlit session state"""
    client.delete(f"/chats/{chat_id}")
    get_chats()
    select_chat(None)
    return


def render_message(message: db.ChatMessage | schema.ChatMessagePlaceholder) -> None:
    """Display a single chat message (either str or Generator)"""
    # Display chat messages from history on app rerun
    role = message.role
    col_message, col_delete = st.columns([0.975, 0.02], vertical_alignment="bottom")
    with col_message:
        with st.chat_message(role):
            if isinstance(message.content, str):
                st.markdown(message.content)
            else:
                st.write_stream(message.content)
    with col_delete:
        if isinstance(message, schema.ChatMessagePlaceholder):
            callback_kwargs = {}
        else:
            callback_kwargs = {
                "on_click": delete_message,
                "kwargs": {"message_id": message.id},
            }
        st.button(
            ":material/delete:",
            help="Delete",
            key=f"delete_{message.id}_{uuid4().hex}",
            use_container_width=True,
            type="tertiary",
            **callback_kwargs,
        )
    return


def delete_message(message_id: str) -> None:
    """Delete a single message from db and refresh streamlit state session"""
    client.delete(f"messages/{message_id}")
    select_chat(st.session_state.chat.id)
    return None


def streaming(chat_id: str, message: str):
    """Stream response"""
    with client.stream(
        "POST",
        f"/chats/{chat_id}/stream",
        json={"content": message},
    ) as r:
        for chunk in r.iter_text():
            yield chunk
