from fastapi import FastAPI
from pydantic import BaseModel
import random

app = FastAPI()

class TextInput(BaseModel):
    text: str

@app.post("/get-senti-score/")
async def process_text(input: TextInput):
    # Dummy processing
    return {"result": random.uniform(0,1)}
