import os, logging, requests
from bardapi import Bard as BardAPI  # type: ignore
import bardapi.constants  # type: ignore

from ink.ink_types import BardResponse


class Bard:
    def __init__(
        self,
        token: str,
        conversationId: str | None = None,
        session: requests.Session | None = None,
    ) -> None:
        self.__logger: logging.Logger = logging.getLogger()
        self.__logger.debug('conversation id: ' + str(conversationId))
        self.__logger.debug('existing session: ' + str(session != None))
        self.__bard: BardAPI = BardAPI(
            token=token, conversation_id=conversationId, session=session
        )

    def sendMessage(self, message: str) -> BardResponse:
        response: BardResponse = BardResponse(**self.__bard.get_answer(message))
        self.__logger.debug(response.content)
        return response

    @staticmethod
    def createSession(tokenIdentifier: str, token: str) -> requests.Session:
        session: requests.Session = requests.Session()
        session.headers = bardapi.constants.SESSION_HEADERS
        session.cookies.set(tokenIdentifier, token)  # type: ignore
        return session
