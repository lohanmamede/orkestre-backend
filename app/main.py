# app/main.py
from fastapi import FastAPI

app = FastAPI(title="Umamão Agenda API")

@app.get("/")
async def root():
    return {"message": "Bem-vindo à API Umamão Agenda!"}