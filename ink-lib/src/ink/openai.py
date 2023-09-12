import logging
from dataclasses import asdict
from typing import Any
import openai  # type: ignore
from ink.ink_types import Role, OpenAIMessage, OpenAIResponse, ChatbotResponse


class OpenAI:
    def __init__(
        self,
        API_key: str,
        model: str = "gpt-3.5-turbo",
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> None:
        self.model: str = model
        self.max_tokens: int = max_tokens
        self.temperature: float = temperature
        openai.api_key = API_key
        self.__logger: logging.Logger = logging.getLogger()
        self.__messages: list[OpenAIMessage] = []
        self.__add_message(
            OpenAIMessage(role=Role.SYSTEM, content="You are a helpful assistant.")
        )

    def __add_message(self, message: OpenAIMessage) -> None:
        self.__messages.append(message)

    def sendMessage(self, message: str) -> ChatbotResponse:
        self.__add_message(OpenAIMessage(role=Role.ASSISTANT, content=message))
        response: Any = openai.ChatCompletion.create(  # type: ignore
            model=self.model,
            messages=list(map(lambda message: asdict(message), self.__messages)),
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        openAIResponse: OpenAIResponse = OpenAIResponse(**response)
        self.__add_message(openAIResponse.message)
        self.__logger.debug(openAIResponse)
        return response
