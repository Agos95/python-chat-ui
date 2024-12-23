import gradio as gr
import httpx


def streaming(message: str, hist: list[dict[str, str]]):
    chat_id = "greager"
    msg = ""
    with httpx.Client() as client:
        with client.stream(
            "POST",
            f"http://localhost:8000/chats/{chat_id}/chat",
            json={"message": message},
        ) as r:
            for chunk in r.iter_text():
                msg += chunk
                yield msg


demo = gr.ChatInterface(fn=streaming, type="messages")

if __name__ == "__main__":
    demo.launch()
