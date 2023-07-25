from types import SimpleNamespace
from inkserver.inkserver import app
from fastapi.testclient import TestClient
from httpx import Response
from inkserver.inkserver_types import Message

client = TestClient(app)


def test_sendMessage() -> None:
    response: Response = client.post('/sendMessage', json={'message': 'hello world'})
    assert response.status_code == 200
    message: Message = response.json(object_hook=lambda x: SimpleNamespace(**x))
    assert type(message.message) == str and len(message.message) > 0
