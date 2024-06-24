import random

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class TextInput(BaseModel):
    text: str


@app.post("/get-senti-score/")
async def get_senti_score(input: TextInput):
    # Dummy processing
    return {"result": random.uniform(0, 1)}

@app.post("/send-alert/")
async def send_alert(input: TextInput):
    print(f"Got alert: {input.text}")
    return {"message":"Alert received"}
