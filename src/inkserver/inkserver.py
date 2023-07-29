import base64, json
from urllib.parse import unquote
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from ink.ink import Ink
from inkserver.inkserver_types import (
    Message,
    Signature,
    SignedMessages,
    Time,
    Verified,
    Timestamp,
)
from ink.ink_types import InkMessage

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
def readMessages(messages: list[InkMessage]) -> JSONResponse:
    ink: Ink = Ink()
    return JSONResponse(content={'signature': ink.signMessages(messages)})


@app.post("/getTimestamp", response_model=Timestamp)
def getTimeStamp(signedMessages: SignedMessages) -> JSONResponse:
    ink: Ink = Ink()
    return JSONResponse(
        content={'timestamp': ink.getTimestamp(signedMessages.signedMessages)}
    )


@app.get(
    "/verifySignature",
    response_model=Verified,
)
def readSignature(messages: str, signedMessages: str, timestamp: str) -> JSONResponse:
    ink: Ink = Ink()
    return JSONResponse(
        content={
            'verified': ink.verifySignature(
                unquote(signedMessages),
                json.loads(
                    base64.b64decode(unquote(messages).encode('utf-8')),
                    object_hook=lambda x: InkMessage(**x),
                ),
            )
            and ink.verifyTimestamp(signedMessages, unquote(timestamp))
        }
    )


@app.post("/extractTime")
def extractTime(timestamp: Timestamp) -> Time:
    ink: Ink = Ink()
    return Time(time=ink.extractTime(unquote(timestamp.timestamp)))
