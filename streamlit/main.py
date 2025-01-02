# from http_client import client
import httpx

import streamlit as st
from app.database.database import Chat


@st.cache_resource
def get_httpx_client():
    return httpx.Client(base_url="http://localhost:8000")


client = get_httpx_client()

title = st.title("Chat App")


if "chats" not in st.session_state:
    chats = client.get("/chats").json()
    chats = [Chat.model_validate(chat) for chat in chats]
    st.session_state.chats = {chat.id: chat for chat in chats}
    st.session_state.chat = None
    st.session_state.history = None


def select_chat(chat_id=None):
    if chat_id is not None:
        st.session_state.chat = st.session_state.chats[chat_id]
        history = client.get(f"/chats/{chat_id}/messages").json()
        st.session_state.history = history
    else:
        st.session_state.chat = None
        st.session_state.history = None
    return


with st.sidebar:
    with st.container(height=500, border=False):
        for chat in st.session_state.chats.values():
            st.button(
                chat.title,
                type="secondary",
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

# st.html(CSS)

is_chat_selected = st.session_state.chat is not None


def delete_message(message_id: str):
    client.delete(f"messages/{message_id}")
    select_chat(st.session_state.chat.id)


if is_chat_selected:
    title.title(f"{st.session_state.chat.title}")
    if st.session_state.history is not None:
        for message in st.session_state.history:
            # Display chat messages from history on app rerun
            role = message["role"]
            col_message, col_delete = st.columns(
                [0.975, 0.025], vertical_alignment="bottom"
            )
            with col_message:
                with st.chat_message(role):
                    st.markdown(message["content"])
            with col_delete:
                st.button(
                    "",
                    help="Delete",
                    on_click=delete_message,
                    kwargs={"message_id": message["id"]},
                    icon=":material/delete:",
                    key=f"delete_{message["id"]}",
                    use_container_width=True,
                    type="tertiary",
                )

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
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    # st.session_state.history.append({"role": "user", "content": prompt})

    # Response
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        with st.spinner(text=""):
            stream = streaming(st.session_state.chat.id, prompt)
            response = st.write_stream(stream)
    # Add assistant response to chat history
    # st.session_state.history.append({"role": "assistant", "content": response})
    select_chat(chat_id=st.session_state.chat.id)
