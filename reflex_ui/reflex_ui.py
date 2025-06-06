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
        display="inline-block",
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


def index() -> rx.Component:
    return rx.flex(
        sidebar(),
        rx.container(
            rx.flex(
                rx.foreach(State.chat, chat_message),
                direction="column",
            ),
        ),
        direction="row",
        align="stretch",
    )


app = rx.App()
app.add_page(index)
