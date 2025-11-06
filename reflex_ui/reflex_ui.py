"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import json

import reflex as rx

# from app.main import app as backend_app
from reflex_ui.schema import ChatMessageSchema
from rxconfig import config

from .sidebar import sidebar

with open("conversations.json", "r") as f:
    _CHAT = json.load(f)[0]


class State(rx.State):
    chat: list[ChatMessageSchema] = _CHAT


def chat_message(message: ChatMessageSchema) -> rx.Component:
    common_style = dict(
        margin_y="0.5em",
        border_radius="10px",
        padding="1em",
        # display="inline-block",
    )

    def ai_message(content: str) -> rx.Component:
        style = common_style | dict(
            text_align="left",
            margin_right="15%",
            background_color=rx.color("accent", 6),
        )
        return rx.box(
            rx.text(content, style=style),
            text_align="left",
        )

    def human_message(content: str) -> rx.Component:
        style = common_style | dict(
            text_align="right",
            margin_left="15%",
            background_color=rx.color("gray", 4),
        )
        return rx.box(
            rx.text(content, style=style),
            text_align="right",
        )

    return rx.cond(
        message["role"] == "ai",
        ai_message(message["content"]),
        human_message(message["content"]),
    )


# def index() -> rx.Component:
#     return rx.box(
#         rx.flex(
#             sidebar(),
#             rx.box(
#                 rx.vstack(
#                     rx.foreach(State.chat, chat_message),
#                     direction="column",
#                 ),
#             ),
#             height="100%",
#         ),
#         height="100vh",
#     )


def chat_list_sidebar():
    """
    A sidebar to display a list of chats.
    This is a placeholder and does not contain actual chat items.
    """
    return rx.box(
        rx.vstack(
            rx.heading("Chats", size="5", padding_bottom="0.5em"),
            rx.box(
                rx.text("Chat 1"),
                bg="#e0e0e0",
                padding="0.5em",
                border_radius="md",
                width="100%",
            ),
            rx.box(
                rx.text("Chat 2"),
                bg="#e0e0e0",
                padding="0.5em",
                border_radius="md",
                width="100%",
            ),
            rx.box(
                rx.text("Chat 3"),
                bg="#e0e0e0",
                padding="0.5em",
                border_radius="md",
                width="100%",
            ),
            spacing="4",
            align_items="stretch",  # Ensures children take full width
        ),
        padding="1em",
        height="100vh",
        width="16em",
        border_right="1px solid #e0e0e0",
        position="sticky",
        top="0px",
        left="0px",
    )


def chat_message_area():
    """
    The area where chat messages will be displayed.
    This box contains simulated message bubbles.
    """
    return rx.box(
        rx.vstack(
            # Left-aligned (received) message bubble
            rx.hstack(
                rx.box(
                    "Hello! How can I help you today?",
                    bg="#e0e0e0",
                    padding="0.5em 1em",
                    border_radius="15px 15px 15px 0",
                ),
                width="100%",
                justify="start",
            ),
            # Right-aligned (sent) message bubble
            rx.hstack(
                rx.box(
                    "Hi, I wanted to ask about the Reflex library.",
                    bg="#007bff",
                    color="white",
                    padding="0.5em 1em",
                    border_radius="15px 15px 0 15px",
                ),
                width="100%",
                justify="end",
            ),
            # Another left-aligned message
            rx.hstack(
                rx.box(
                    "Of course! It's a powerful framework for building web apps in pure Python.",
                    bg="#e0e0e0",
                    padding="0.5em 1em",
                    border_radius="15px 15px 15px 0",
                ),
                width="100%",
                justify="start",
            ),
            # Another right-aligned message
            rx.hstack(
                rx.box(
                    "Awesome, where can I find the documentation?",
                    bg="#007bff",
                    color="white",
                    padding="0.5em 1em",
                    border_radius="15px 15px 0 15px",
                ),
                width="100%",
                justify="end",
            ),
            spacing="5",
            width="100%",
        ),
        flex_grow=1,
        width="100%",
        padding="1em",
        overflow_y="auto",  # Allows scrolling if messages overflow
    )


def text_input_area():
    """
    The area at the bottom for typing and sending a message.
    """
    return rx.box(
        rx.text("Text input field will be here..."),
        padding="1em",
        width="100%",
        border_top="1px solid #e0e0e0",
    )


def main_chat_window():
    """
    The main window containing the message area and the text input area.
    This uses a vstack to arrange its children vertically.
    """
    return rx.vstack(
        chat_message_area(),
        text_input_area(),
        height="100vh",
        width="100%",
        spacing="0",  # Remove space between message area and input
    )


@rx.page(route="/")
def chat_app():
    """
    The main page that combines the sidebar and the chat window.
    """
    return rx.flex(
        chat_list_sidebar(),
        main_chat_window(),
        height="100vh",  # Make the layout take the full viewport height
        width="100%",
        spacing="0",  # Remove space between sidebar and main window
    )


app = rx.App(theme=rx.theme(accent_color="blue"))
# app.add_page(index)


rx.call_script
