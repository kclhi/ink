import base64, json
import pytest  # type: ignore
from datetime import datetime
from typing import Any
import urllib.parse
from zoneinfo import ZoneInfo
from fastapi.testclient import TestClient
from httpx import Response

from inkserver.inkserver import app
from inkserver.inkserver_types import Message, Signature, Time, Timestamp, Verified
from ink.ink_types import InkMessage


@pytest.fixture
def mock_sendMessage(mocker: Any) -> None:
    return mocker.patch(
        'ink.ink.Ink.sendMessage',
        return_value=InkMessage(sender='chatbot', text='bar', conversationId='baz'),
    )


def sendMessage(client: TestClient) -> None:
    response: Response = client.post('/sendMessage', json={'message': 'foo'})
    assert response.status_code == 200
    message: Message = Message(message=response.json()['message'])
    assert (
        type(message.message) == str
        and len(message.message) > 0
        and message.message == 'bar'
    )


def signMessages(client: TestClient) -> Signature:
    response: Response = client.post('/signMessages')
    assert response.status_code == 200
    signature: Signature = response.json(object_hook=lambda d: Signature(**d))
    assert type(signature.signature) == str and len(signature.signature) > 0
    return signature


def getTimestamp(client: TestClient) -> Timestamp:
    response: Response = client.post(
        '/getTimestamp', json={'signedMessages': signMessages(client).signature}
    )
    assert response.status_code == 200
    timestamp: Timestamp = response.json(object_hook=lambda d: Timestamp(**d))
    assert type(timestamp.timestamp) == str and len(timestamp.timestamp) > 0
    return timestamp


def test_sendMessage(mock_sendMessage: Any) -> None:
    client: TestClient = TestClient(app)
    sendMessage(client)


def test_signMessages(mock_sendMessage: Any) -> None:
    client: TestClient = TestClient(app)
    sendMessage(client)
    signMessages(client)


def test_getTimestamp(mock_sendMessage: Any) -> None:
    client: TestClient = TestClient(app)
    sendMessage(client)
    getTimestamp(client)


def test_verifySignature(mock_sendMessage: Any) -> None:
    client = TestClient(app)
    sendMessage(client)
    response: Response = client.get(
        '/verifySignature?messages='
        + urllib.parse.quote(
            base64.b64encode(
                json.dumps(
                    [
                        InkMessage(sender='user', text='foo'),
                        InkMessage(sender='chatbot', text='bar'),
                    ],
                    default=lambda o: o.__dict__,
                ).encode('utf-8')
            ).decode('utf-8'),
            safe='',
        )
        + '&signedMessages='
        + urllib.parse.quote(signMessages(client).signature, safe='')
        + '&timestamp='
        + urllib.parse.quote(getTimestamp(client).timestamp, safe='')
    )
    assert response.status_code == 200
    verified: Verified = response.json(object_hook=lambda x: Verified(**x))
    assert type(verified.verified) == bool and verified.verified


def test_extractTime(mock_sendMessage: Any) -> None:
    client = TestClient(app)
    sendMessage(client)
    timeNow: datetime = datetime.now(tz=ZoneInfo('UTC'))
    response: Response = client.post(
        '/extractTime',
        json={'timestamp': urllib.parse.quote(getTimestamp(client).timestamp, safe='')},
    )
    assert response.status_code == 200
    time: Time = response.json(object_hook=lambda x: Time(**x))
    assert (
        type(time.time) == datetime
        and time.time.hour == timeNow.hour
        and time.time.minute == timeNow.minute
    )
