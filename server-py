from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List

app = FastAPI()

rooms: Dict[str, List[str]] = {}


class Message(BaseModel):
    room: str
    msg: str


@app.post("/send")
def send_message(message: Message):
    rooms.setdefault(message.room, []).append(message.msg)
    return {"status": "ok"}


@app.get("/messages/{room}")
def get_messages(room: str):
    return rooms.get(room, [])
