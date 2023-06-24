from typing import Annotated
from fastapi import Body, FastAPI
from backend.parser.parser import parser

app = FastAPI()

def buildCommand(command, **params) -> str:
  for param in params.keys():
    command += f' -{param}->{params[param]}'
  return command

@app.post('/interpret/{command}/')
async def interpret(command:str, params: Annotated[dict, Body()]):
  command = buildCommand(command, **params)
  return {'message': parser.parse(command)}