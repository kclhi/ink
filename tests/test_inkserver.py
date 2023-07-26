import json
import urllib.parse
from functools import reduce
from fastapi.testclient import TestClient
from httpx import Response

from inkserver.inkserver import app
from inkserver.inkserver_types import Message, Signature, Verified

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


def test_verifySignature() -> None:
    response: Response = client.get(
        '/verifySignature/'
        + urllib.parse.quote(
            json.dumps([{'sender': 'user', 'text': 'hello world'}]), safe=''
        )
        + '/'
        + urllib.parse.quote(test_signMessages().signature, safe='')
    )
    assert response.status_code == 200
    verified: Verified = response.json(object_hook=lambda x: Verified(**x))
    assert type(verified.verified) == bool and verified.verified
