from pydantic import BaseModel


class Message(BaseModel):
    message: str


class Signature(BaseModel):
    signature: str


class Verified(BaseModel):
    verified: bool
