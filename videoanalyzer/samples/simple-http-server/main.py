from typing import Any, List
from fastapi import FastAPI, File, Form, UploadFile

app = FastAPI()

@app.post("/analyze")
async def analyze(data: str = Form(), file: UploadFile = File()) -> Any:
    print(data)
    print(file.filename)
    return {'prop1': 'value1'}

@app.get("/healthz")
async def healthz() -> str:
    return "Ok"