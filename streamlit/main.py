import chat as ch
import schema

import streamlit as st
from app.database import database as db

# ===============
# == STREAMLIT ==
# ===============

title = st.title("Chat App")


if "chats" not in st.session_state:
    ch.get_chats()
    ch.select_chat(None)


# -- Sidebar --
# -------------

with st.sidebar:
    st.button(
        "New Chat",
        help="New",
        icon=":material/add:",
        on_click=ch.create_chat,
        use_container_width=False,
        type="tertiary",
    )
    for chat in st.session_state.chats.values():
        col_title, col_delete = st.columns([0.975, 0.02])
        with col_title:
            st.button(
                chat.title or "New Chat",
                type="secondary",
                use_container_width=True,
                on_click=ch.select_chat,
                kwargs={"chat_id": chat.id},
            )
        with col_delete:
            st.button(
                "",
                help="Delete",
                on_click=ch.delete_chat,
                kwargs={"chat_id": chat.id},
                icon=":material/delete:",
                key=f"delete_{chat.id}",
                use_container_width=True,
                type="tertiary",
            )

# -- Main window --
# -----------------

is_chat_selected = st.session_state.chat is not None


if is_chat_selected:
    ch.render_chat()
    prompt = st.chat_input()

else:
    prompt = st.chat_input("Select a chat", disabled=True)


# React to user input
if prompt:
    # since we do not know message_id (it is generated by the backend)
    # initially use a placeholder container to show input, response,
    # and a fake delete button
    placeholder = st.empty()
    with placeholder.container():
        user_message = schema.ChatMessagePlaceholder(
            content=prompt, role=db.ChatMessageRole.HUMAN
        )
        ch.render_message(user_message)
        # Response
        ai_message = schema.ChatMessagePlaceholder(
            content=ch.streaming(st.session_state.chat.id, prompt),
            role=db.ChatMessageRole.AI,
        )
        ch.render_message(ai_message)

    # now query again the db to get the actual list of messages
    # and rerender the last two messages, with the correct ids
    # TODO: add an endpoint to get only the last two messages
    # instead of the whole history from the db
    ch.select_chat(st.session_state.chat.id)
    for message in st.session_state.history[-2:]:
        ch.render_message(message)
    # now remove the placeholder container
    # (if you put it before the for loop, some weird scroll happens in the ui)
    placeholder.empty()
