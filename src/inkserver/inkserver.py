from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from ink.ink import Ink
from inkserver.inkserver_types import Message

load_dotenv()
app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/sendMessage", response_model=Message)
def read_message(message: Message) -> JSONResponse:
    ink: Ink = Ink()
    return JSONResponse(content={'message': ink.sendMessage(message.message)})
