import base64, json, os
from dataclasses import asdict
from typing import cast
from urllib.parse import unquote
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from configparser import ConfigParser

from ink.ink import Ink
from ink.llama2 import Llama2
from inkserver.inkserver_types import (
    Message,
    Signature,
    SignedMessages,
    Time,
    Verified,
    Timestamp,
)
from ink.ink_types import InkMessage
from llama2.llama2_types import Llama2ChatExchange

load_dotenv()
app: FastAPI = FastAPI()

config: ConfigParser = ConfigParser()
config.read(
    f'config/config.{os.environ["ENV"] if "ENV" in os.environ.keys() else "dev"}.ini'
)

origins = [config.get('URLS', 'ORIGIN', vars=os.environ)]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.add_middleware(
    SessionMiddleware,
    secret_key=config.get('COOKIE', 'SESSION_KEY', vars=os.environ),
    session_cookie=config.get('COOKIE', 'NAME'),
    same_site=config.get('COOKIE', 'SAME_SITE'),
    https_only=config.get('COOKIE', 'HTTPS') == 'True',
    max_age=None,
)


@app.post('/sendMessage', response_model=Message)
def readMessage(message: Message, request: Request) -> JSONResponse:
    request.session.setdefault('messages', []).append(
        asdict(InkMessage(sender='user', text=message.message)),
    )
    llama2: Llama2 = Llama2(
        apiURL=config.get('URLS', 'API_URL'),
        chat=list(
            map(
                lambda o: Llama2ChatExchange(**o),
                json.loads(request.session['prompts']),
            )
        )
        if 'prompts' in request.session.keys()
        else None,
    )
    ink: Ink = Ink(
        llama2,
        config.get('SIGNING', 'PRIVATE_KEY_PATH', vars=os.environ),
        config.get('SIGNING', 'CERTIFICATE_PATH', vars=os.environ),
        config.get('SIGNING', 'TSA_CERTIFICATE_PATH', vars=os.environ),
    )
    response: InkMessage = ink.sendMessage(message.message)
    request.session.setdefault('messages', []).append(
        asdict(InkMessage(sender=response.sender, text=response.text)),
    )
    request.session['prompts'] = json.dumps(
        list(map(lambda o: asdict(o), llama2.getChat()))
    )
    return JSONResponse(content={'message': response.text})


@app.post('/signMessages', response_model=Signature)
def readMessages(request: Request) -> JSONResponse:
    if 'messages' not in request.session.keys() or (
        'messages' in request.session.keys()
        and len(str(request.session.get('messages'))) == 0
    ):
        raise HTTPException(status_code=500, detail='Nothing to sign')
    ink: Ink = Ink(
        Llama2(apiURL=config.get('URLS', 'API_URL')),
        config.get('SIGNING', 'PRIVATE_KEY_PATH', vars=os.environ),
        config.get('SIGNING', 'CERTIFICATE_PATH', vars=os.environ),
        config.get('SIGNING', 'TSA_CERTIFICATE_PATH', vars=os.environ),
    )
    inkMessages: list[InkMessage] = [
        InkMessage(**message)
        for message in cast(list[dict[str, str]], request.session.get('messages'))
    ]
    return JSONResponse(content={'signature': ink.signMessages(inkMessages)})


@app.post('/getTimestamp', response_model=Timestamp)
def getTimeStamp(signedMessages: SignedMessages) -> JSONResponse:
    ink: Ink = Ink(
        Llama2(apiURL=config.get('URLS', 'API_URL')),
        config.get('SIGNING', 'PRIVATE_KEY_PATH', vars=os.environ),
        config.get('SIGNING', 'CERTIFICATE_PATH', vars=os.environ),
        config.get('SIGNING', 'TSA_CERTIFICATE_PATH', vars=os.environ),
    )
    return JSONResponse(
        content={'timestamp': ink.getTimestamp(signedMessages.signedMessages)}
    )


@app.get(
    '/verifySignature',
    response_model=Verified,
)
def readSignature(messages: str, signedMessages: str, timestamp: str) -> JSONResponse:
    ink: Ink = Ink(
        Llama2(apiURL=config.get('URLS', 'API_URL')),
        config.get('SIGNING', 'PRIVATE_KEY_PATH', vars=os.environ),
        config.get('SIGNING', 'CERTIFICATE_PATH', vars=os.environ),
        config.get('SIGNING', 'TSA_CERTIFICATE_PATH', vars=os.environ),
    )
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
    ink: Ink = Ink(
        Llama2(apiURL=config.get('URLS', 'API_URL')),
        config.get('SIGNING', 'PRIVATE_KEY_PATH', vars=os.environ),
        config.get('SIGNING', 'CERTIFICATE_PATH', vars=os.environ),
        config.get('SIGNING', 'TSA_CERTIFICATE_PATH', vars=os.environ),
    )
    return Time(time=ink.extractTime(unquote(timestamp.timestamp)))
