from datetime import datetime
from pydantic import BaseModel


class Message(BaseModel):
    message: str


class Signature(BaseModel):
    signature: str


class Verified(BaseModel):
    verified: bool


class Timestamp(BaseModel):
    timestamp: str


class SignedMessages(BaseModel):
    signedMessages: str


class Time(BaseModel):
    time: datetime
