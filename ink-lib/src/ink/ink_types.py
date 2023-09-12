from dataclasses import dataclass
from typing import Protocol
from enum import Enum


@dataclass
class BardChoice:
    id: str
    content: list[str]


@dataclass
class ChatbotResponse:
    def __init__(self, content: str, conversation_id: str):
        self.content = content
        self.conversation_id = conversation_id

    @property
    def content(self) -> str:
        return self.content

    @content.setter
    def content(self, value: str) -> None:
        self.content = value


@dataclass
class BardResponse(ChatbotResponse):
    response_id: str
    factualityQueries: str | None
    textQuery: list[str | int]
    choices: list[str]
    links: list[str]
    images: set[str]
    code: str | None
    langCode: str


class Role(str, Enum):
    USER = "user"
    SYSTEM = "system"
    ASSISTANT = "assistant"


@dataclass
class OpenAIMessage:
    role: Role
    content: str


@dataclass
class OpenAIChoice:
    index: int
    message: OpenAIMessage
    finish_reason: str


@dataclass
class OpenAIResponse(ChatbotResponse):
    choices: list[OpenAIChoice]
    created: int
    id: str
    model: str
    object: str
    usage: dict[str, int]

    @property
    def message(self) -> OpenAIMessage:
        return self.choices[0].message

    @property
    def content(self) -> str:
        return self.message.content.strip()

    @content.setter
    def content(self, value: str) -> None:
        self.content = value


@dataclass
class InkMessage:
    sender: str
    text: str
    conversationId: str | None = None


class Chatbot(Protocol):
    def sendMessage(self, message: str) -> ChatbotResponse:
        ''''''
