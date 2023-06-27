from fastapi import FastAPI
from pydantic import BaseModel
from backend.parser.parser import parser

app = FastAPI()
class parser_call_body(BaseModel):
  command: str

@app.post('/interpret/')
async def interpret(body: parser_call_body):
  message = parser.parse(body.command.strip())
  if message == None:
    return {'message': 'Error de sintaxis'}
  return {'message': message}