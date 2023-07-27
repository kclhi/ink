from datetime import datetime
import logging, os, base64, json
from typing import cast
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends.openssl.rsa import RSAPublicKey
from rfc3161ng import RemoteTimestamper, get_timestamp  # type: ignore

from ink.bard import Bard
from ink.ink_types import Chatbot, InkMessage


class Ink:
    def __init__(self) -> None:
        self.__logger: logging.Logger = logging.getLogger()

    def sendMessage(self, message: str) -> str:
        bard: Chatbot = Bard()
        return bard.sendMessage(message)

    def signMessages(self, messages: list[InkMessage]) -> str:
        self.__logger.debug(messages)
        with open(os.environ['privateKeyPath'], 'rb') as pemFile:
            privateKey: bytes = pemFile.read()
        signedMessage: bytes = load_pem_private_key(privateKey, password=None).sign(
            json.dumps(messages, default=lambda o: o.__dict__).encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        encodedSignedMessage: str = base64.b64encode(signedMessage).decode('utf-8')
        self.__logger.debug(encodedSignedMessage)
        return encodedSignedMessage

    def verifySignature(self, signedMessages: str, messages: list[InkMessage]) -> bool:
        self.__logger.debug(signedMessages)
        self.__logger.debug(messages)
        with open(os.environ['certificatePath'], 'rb') as pemFile:
            certificate: bytes = pemFile.read()
        publicKey: RSAPublicKey = cast(
            RSAPublicKey, load_pem_x509_certificate(certificate).public_key()
        )
        try:
            publicKey.verify(
                base64.b64decode(signedMessages.encode('utf-8')),
                json.dumps(messages, default=lambda o: o.__dict__).encode('utf-8'),
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
            return True
        except:
            return False

    def getTimestamp(self, signedMessages: str) -> str:
        timestamp: str = base64.b64encode(
            RemoteTimestamper(
                'https://freetsa.org/tsr',
                certificate=open(os.environ['tsaCertificatePath'], 'rb').read(),
                hashname='sha512',
            ).timestamp(data=base64.b64decode(signedMessages.encode('utf-8')))
        ).decode('utf-8')
        self.__logger.debug(timestamp)
        return timestamp

    def verifyTimestamp(self, signedMessages: str, timestamp: str) -> bool:
        try:
            RemoteTimestamper(
                'https://freetsa.org/tsr',
                certificate=open(os.environ['tsaCertificatePath'], 'rb').read(),
                hashname='sha512',
            ).check(
                base64.b64decode(timestamp.encode('utf-8')),
                data=base64.b64decode(signedMessages.encode('utf-8')),
            )
            return True
        except:
            return False

    def extractTime(self, timestamp: str) -> datetime:
        return get_timestamp(base64.b64decode(timestamp.encode('utf-8')))
