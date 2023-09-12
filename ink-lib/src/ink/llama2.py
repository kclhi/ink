import logging
from typing import Any
from llama2.llama2 import Llama2 as Llama2API

from ink.ink_types import ChatbotResponse


class Llama2:
    def __init__(
        self, apiURL: str = 'http://127.0.0.1:8080', chat: list[Any] | None = None
    ) -> None:
        self.__logger: logging.Logger = logging.getLogger()
        self.__llama2: Llama2API = Llama2API(apiURL, chat)

    def sendMessage(self, message: str) -> ChatbotResponse:
        self.__llama2.chatCompletion(message)
        response: ChatbotResponse = ChatbotResponse(
            content=self.__llama2.getChat()[-1].assistant, conversation_id=''
        )
        self.__logger.debug(response.content)
        return response

    def getChat(self) -> list[Any]:
        return self.__llama2.getChat()
