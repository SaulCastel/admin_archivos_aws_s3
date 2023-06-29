from fastapi import FastAPI
from pydantic import BaseModel
from os import makedirs
from backend.parser.parser import parser
from backend.commands import cloud, local
from config import files_dir

app = FastAPI()
class parser_call_body(BaseModel):
  command: str

class backup_body(BaseModel):
  type: str
  path: str
  name: str | None
  body: str | None

class name_body(BaseModel):
  name: str

@app.post('/interpret/')
async def interpret(body: parser_call_body):
  message = parser.parse(body.command.strip())
  if message == None:
    return {'message': 'Error de sintaxis'}
  return {'message': message}

@app.post('/open/{type}/')
async def send_file_contents(type:str, body:name_body):
  data = ''
  if type == 'server':
    data = local.open_file(body.name)
  else:
    data = cloud.open_file(body.name)
  return {'content': data}

@app.post('/backup/server/')
async def backup_to_server(body: backup_body):
  path = files_dir + body.path
  if body.type == 'dir':
    makedirs(path, exist_ok=True)
    return {'message': 'Carpeta creada'}
  makedirs(path, exist_ok=True)
  with open(path+body.name, 'w') as file:
    file.write(body.body)
    return {'message': 'Archivo creado'}

@app.post('/recovery/server/')
async def recover_server_files(body:name_body):
  file_tree = local.recover_server_files(body.name)
  return {'list': file_tree}