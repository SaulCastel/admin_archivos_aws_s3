from fastapi import FastAPI
from backend.parser.parser import parser

app = FastAPI()

@app.get('/interpret/')
async def interpret(command:str):
  return {'message': parser.parse(command)}