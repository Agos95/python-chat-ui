import schema
from settings import ui_settings

import streamlit as st
from app.database import database as db

# this must be run before any other streamlit command
# even if in other files
st.set_page_config(
    page_title=ui_settings.APP_TITLE,
    page_icon=ui_settings.APP_FAVICON,
    layout="centered",
)

import chat as ch  # noqa: E402

# ===============
# == STREAMLIT ==
# ===============

# get primary color
ST_PRIMARY_COLOR = st.get_option("theme.primaryColor")


if "title" not in st.session_state:
    st.session_state.title = ui_settings.APP_TITLE

st.subheader(st.session_state.title, divider="red")


if "chats" not in st.session_state:
    ch.get_chats()
    ch.select_chat(None)


# -- Sidebar --
# -------------
CHAT_LIST_KEY = "chat-list"
with st.sidebar:
    st.button(
        "New Chat",
        help="New",
        icon=":material/add:",
        on_click=ch.create_chat,
        use_container_width=False,
        type="tertiary",
    )
    with st.container(key=CHAT_LIST_KEY):
        for chat in st.session_state.chats.values():
            col_title, col_edit, _, col_delete = st.columns([50, 5, 1, 5])
            with col_title:
                st.button(
                    chat.title or "New Chat",
                    type="tertiary",
                    use_container_width=True,
                    on_click=ch.select_chat,
                    key=f"{chat.id}",
                    kwargs={"chat_id": chat.id},
                )
            with col_edit:
                st.button(
                    "",
                    help="Edit",
                    on_click=ch.set_title,
                    kwargs={"chat_id": chat.id},
                    icon=":material/edit:",
                    key=f"edit_{chat.id}",
                    use_container_width=True,
                    type="tertiary",
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


# custom CSS for chat list
st.html(f"""
    <style>
        /* reduce gap between buttons */
        .st-key-{CHAT_LIST_KEY} {{
            gap: .25rem
        }}

        /* don't use rounded corners */ 
        .st-key-{CHAT_LIST_KEY} button {{
            border-radius: 0px
        }}

        /* color and add border when chat is selected */
        .st-key-{CHAT_LIST_KEY} button:focus {{
            color: {ST_PRIMARY_COLOR};
            border-bottom: 1px solid;
        }}
    </style>
    """)

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
