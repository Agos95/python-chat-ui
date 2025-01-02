from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import uvicorn

from .chat import router as chat_router
from .message import router as message_router

app = FastAPI()
app.include_router(chat_router)
app.include_router(message_router)


@app.get("/", include_in_schema=False)
async def home() -> RedirectResponse:
    return RedirectResponse("/docs")


if __name__ == "__main__":
    uvicorn.run(app, reload=True)
