# data from: https://huggingface.co/datasets/smangrul/ultrachat-10k-chatml

import json

import pandas as pd
from database import ChatMessageRole

splits = {
    "train": "data/train-00000-of-00001.parquet",
    "test": "data/test-00000-of-00001.parquet",
}
df = pd.read_parquet("hf://datasets/smangrul/ultrachat-10k-chatml/" + splits["train"])

chats = df.loc[:9, "messages"].to_list()


def convert_message_role(message: dict) -> dict:
    role = message.get("role", "")
    match role:
        case "user":
            role = ChatMessageRole.HUMAN
        case "assistant":
            role = ChatMessageRole.AI
        case _:
            role = ChatMessageRole.HUMAN
    message["role"] = role
    return message


chats = [[convert_message_role(message) for message in chat] for chat in chats]

with open("conversations.json", "w") as f:
    json.dump(chats, f)
