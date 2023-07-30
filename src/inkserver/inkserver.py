import base64, json, os
from dataclasses import asdict
from typing import cast
from urllib.parse import unquote
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
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
    'https://127.0.0.1:3000',
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ['cookie_sessionKey'],
    session_cookie=os.environ['cookie_name'],
    same_site=os.environ['cookie_sameSite'],
    https_only=os.environ['cookie_https'] == "True",
    max_age=None,
)


@app.post('/sendMessage', response_model=Message)
def readMessage(message: Message, request: Request) -> JSONResponse:
    request.session.setdefault('messages', []).append(
        asdict(InkMessage(sender='user', text=message.message)),
    )
    ink: Ink = Ink()
    response: str = ink.sendMessage(message.message)
    request.session.setdefault('messages', []).append(
        asdict(InkMessage(sender='bot', text=response)),
    )
    return JSONResponse(content={'message': response})


@app.post('/signMessages', response_model=Signature)
def readMessages(request: Request) -> JSONResponse:
    if 'messages' not in request.session.keys() or (
        'messages' in request.session.keys()
        and len(str(request.session.get('messages'))) == 0
    ):
        raise HTTPException(status_code=500, detail='Nothing to sign')
    ink: Ink = Ink()
    inkMessages: list[InkMessage] = [
        InkMessage(**message)
        for message in cast(list[dict[str, str]], request.session.get('messages'))
    ]
    return JSONResponse(content={'signature': ink.signMessages(inkMessages)})


@app.post('/getTimestamp', response_model=Timestamp)
def getTimeStamp(signedMessages: SignedMessages) -> JSONResponse:
    ink: Ink = Ink()
    return JSONResponse(
        content={'timestamp': ink.getTimestamp(signedMessages.signedMessages)}
    )


@app.get(
    '/verifySignature',
    response_model=Verified,
)
def readSignature(messages: str, signedMessages: str, timestamp: str) -> JSONResponse:
    ink: Ink = Ink()
    inkMessages: list[InkMessage] = json.loads(
        base64.b64decode(unquote(messages).encode('utf-8')),
        object_hook=lambda o: InkMessage(**o),
    )
    return JSONResponse(
        content={
            'verified': ink.verifySignature(
                unquote(signedMessages),
                inkMessages,
            )
            and ink.verifyTimestamp(signedMessages, unquote(timestamp))
        }
    )


@app.post('/extractTime')
def extractTime(timestamp: Timestamp) -> Time:
    ink: Ink = Ink()
    return Time(time=ink.extractTime(unquote(timestamp.timestamp)))
