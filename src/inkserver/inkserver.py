import json
from typing import cast
import urllib.parse
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from ink.ink import Ink
from inkserver.inkserver_types import Message, Signature, Verified
from ink.ink_types import InkMessages

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
def readMessage(message: Message) -> JSONResponse:
    ink: Ink = Ink()
    return JSONResponse(content={'message': ink.sendMessage(message.message)})


@app.post("/signMessages", response_model=Signature)
def readMessages(messages: list[Message]) -> JSONResponse:
    ink: Ink = Ink()
    return JSONResponse(
        content={
            'signature': ink.signMessages(
                InkMessages(
                    messages=list(map(lambda message: str(message.message), messages))
                )
            )
        }
    )


@app.get("/verifySignature/{messages}/{signature:path}", response_model=Verified)
def readSignature(messages: str, signature: str) -> JSONResponse:
    ink: Ink = Ink()
    return JSONResponse(
        content={
            'verified': ink.verifySignature(
                urllib.parse.unquote(signature),
                InkMessages(
                    messages=list(
                        map(
                            lambda message: str(message.message),
                            cast(
                                list[Message],
                                json.loads(
                                    urllib.parse.unquote(messages),
                                    object_hook=lambda x: Message(**x),
                                ),
                            ),
                        )
                    )
                ),
            )
        }
    )
