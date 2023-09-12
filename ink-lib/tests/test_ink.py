import base64, random, time, requests, os
from zoneinfo import ZoneInfo
import pytest  # type: ignore
from datetime import datetime
from dotenv import load_dotenv

from ink.ink import Ink
from ink.llama2 import Llama2
from ink.ink_types import InkMessage


def getWord() -> str:
    return random.choice(
        [
            'foobar',
            'foo',
            'bar',
            'baz',
            'qux',
            'quux',
            'corge',
            'grault',
            'garply',
            'waldo',
            'fred',
            'plugh',
            'xyzzy',
            'thud',
        ]
    )


@pytest.fixture(scope='session', autouse=True)
def load_env() -> None:
    load_dotenv()


@pytest.fixture()
def wait() -> None:
    time.sleep(10)


def test_sendMessage(wait: None) -> None:
    ink: Ink = Ink(
        Llama2(),
        os.environ['privateKeyPath'],
        os.environ['certificatePath'],
        os.environ['tsaCertificatePath'],
    )
    response: InkMessage = ink.sendMessage('hello world')
    assert type(response.text) == str and len(response.text) > 0


def test_messageContextA(wait: None) -> None:
    inkA: Ink = Ink(
        Llama2(),
        os.environ['privateKeyPath'],
        os.environ['certificatePath'],
        os.environ['tsaCertificatePath'],
    )
    word: str = getWord()
    responseA: InkMessage = inkA.sendMessage('remember the following word: ' + word)
    assert (
        type(responseA.text) == str
        and len(responseA.text) > 0
        and 'ok' in responseA.text.lower()
    )
    time.sleep(10)
    responseB: InkMessage = inkA.sendMessage(
        'what was the word I asked you to remember?'
    )
    assert (
        type(responseB.text) == str
        and len(responseB.text) > 0
        and word in responseB.text.lower()
    )


def test_messageContextB(wait: None) -> None:
    chatbot: Llama2 = Llama2()
    inkB: Ink = Ink(
        chatbot,
        os.environ['privateKeyPath'],
        os.environ['certificatePath'],
        os.environ['tsaCertificatePath'],
    )
    word: str = getWord()
    responseC: InkMessage = inkB.sendMessage('remember the following word: ' + word)
    assert (
        type(responseC.text) == str
        and len(responseC.text) > 0
        and 'ok' in responseC.text.lower()
    )
    time.sleep(10)
    inkC: Ink = Ink(
        Llama2(chat=chatbot.getChat()),
        os.environ['privateKeyPath'],
        os.environ['certificatePath'],
        os.environ['tsaCertificatePath'],
    )
    responseD: InkMessage = inkC.sendMessage(
        'what was the word I asked you to remember?'
    )
    assert (
        type(responseD.text) == str
        and len(responseD.text) > 0
        and word in responseD.text.lower()
    )


def test_signMessage() -> None:
    ink: Ink = Ink(
        Llama2(),
        os.environ['privateKeyPath'],
        os.environ['certificatePath'],
        os.environ['tsaCertificatePath'],
    )
    signedMessages: str = ink.signMessages(
        [InkMessage(sender='bob', text='hello world')]
    )
    assert len(signedMessages) > 0


def test_verifySignature() -> None:
    ink: Ink = Ink(
        Llama2(),
        os.environ['privateKeyPath'],
        os.environ['certificatePath'],
        os.environ['tsaCertificatePath'],
    )
    signedMessages: str = ink.signMessages(
        [InkMessage(sender='bob', text='hello world')]
    )
    assert len(signedMessages) > 0
    assert ink.verifySignature(
        signedMessages, [InkMessage(sender='bob', text='hello world')]
    )
    assert not ink.verifySignature(
        base64.b64encode(bytes('foo', 'utf-8')).decode('utf-8'),
        [InkMessage(sender='bob', text='hello world')],
    )


def test_getTimestamp() -> None:
    ink: Ink = Ink(
        Llama2(),
        os.environ['privateKeyPath'],
        os.environ['certificatePath'],
        os.environ['tsaCertificatePath'],
    )
    signedMessages: str = ink.signMessages(
        [InkMessage(sender='bob', text='hello world')]
    )
    assert len(signedMessages) > 0
    assert len(ink.getTimestamp(signedMessages)) > 0


def test_verifyTimestamp() -> None:
    ink: Ink = Ink(
        Llama2(),
        os.environ['privateKeyPath'],
        os.environ['certificatePath'],
        os.environ['tsaCertificatePath'],
    )
    signedMessages: str = ink.signMessages(
        [InkMessage(sender='bob', text='hello world')]
    )
    assert len(signedMessages) > 0
    timestamp: str = ink.getTimestamp(signedMessages)
    assert len(timestamp) > 0
    assert ink.verifyTimestamp(signedMessages, timestamp)
    assert not ink.verifyTimestamp(
        base64.b64encode(bytes('foo', 'utf-8')).decode('utf-8'), timestamp
    )


def test_extractTime() -> None:
    ink: Ink = Ink(
        Llama2(),
        os.environ['privateKeyPath'],
        os.environ['certificatePath'],
        os.environ['tsaCertificatePath'],
    )
    signedMessages: str = ink.signMessages(
        [InkMessage(sender='bob', text='hello world')]
    )
    assert len(signedMessages) > 0
    timeNow: datetime = datetime.now(tz=ZoneInfo('UTC'))
    timestamp: str = ink.getTimestamp(signedMessages)
    assert len(timestamp) > 0
    timestampTime: datetime = ink.extractTime(timestamp)
    assert timestampTime.hour == timeNow.hour and timestampTime.minute == timeNow.minute
