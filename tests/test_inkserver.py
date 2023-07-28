from datetime import datetime
import json
import urllib.parse
from functools import reduce
from zoneinfo import ZoneInfo
from fastapi.testclient import TestClient
from httpx import Response

from inkserver.inkserver import app
from inkserver.inkserver_types import Message, Signature, Time, Timestamp, Verified

client = TestClient(app)


def test_sendMessage() -> None:
    response: Response = client.post('/sendMessage', json={'message': 'hello world'})
    assert response.status_code == 200
    message: Message = response.json(object_hook=lambda x: Message(**x))
    assert type(message.message) == str and len(message.message) > 0


def test_signMessages() -> Signature:
    response: Response = client.post(
        '/signMessages', json=[{'sender': 'user', 'text': 'hello world'}]
    )
    assert response.status_code == 200
    signature: Signature = response.json(object_hook=lambda x: Signature(**x))
    assert type(signature.signature) == str and len(signature.signature) > 0
    return signature


def test_getTimestamp() -> Timestamp:
    response: Response = client.post(
        '/getTimestamp', json={'signedMessages': test_signMessages().signature}
    )
    assert response.status_code == 200
    timestamp: Timestamp = response.json(object_hook=lambda x: Timestamp(**x))
    assert type(timestamp.timestamp) == str and len(timestamp.timestamp) > 0
    return timestamp


def test_verifySignature() -> None:
    response: Response = client.get(
        '/verifySignature?messages='
        + urllib.parse.quote(
            json.dumps([{'sender': 'user', 'text': 'hello world'}]), safe=''
        )
        + '&signedMessages='
        + urllib.parse.quote(test_signMessages().signature, safe='')
        + '&timestamp='
        + urllib.parse.quote(test_getTimestamp().timestamp, safe='')
    )
    assert response.status_code == 200
    verified: Verified = response.json(object_hook=lambda x: Verified(**x))
    assert type(verified.verified) == bool and verified.verified


def test_extractTime() -> None:
    timeNow: datetime = datetime.now(tz=ZoneInfo('UTC'))
    response: Response = client.post(
        '/extractTime',
        json={'timestamp': urllib.parse.quote(test_getTimestamp().timestamp, safe='')},
    )
    assert response.status_code == 200
    time: Time = response.json(object_hook=lambda x: Time(**x))
    assert (
        type(time.time) == datetime
        and time.time.hour == timeNow.hour
        and time.time.minute == timeNow.minute
    )
