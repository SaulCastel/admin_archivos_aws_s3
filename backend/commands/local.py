import os
import shutil
import requests
import boto3
import json
import config
import backend.commands.cloud as cloud
import re

def create(path, name, body) -> str:
  path = config.basedir + path
  if os.path.isfile(path + name):
    return 'Archivo ya existe'
  elif not os.path.isdir(path):
    os.makedirs(path)
  try:
    file = open(path + name, 'w')
  except IsADirectoryError:
    return 'Ruta especificada no puede ser un directorio'
  else:
    with file:
      file.write(body)
      return 'Archivo creado exitosamente'

def open_file(name, ip=None, port=None) -> str:
  if ip and port:
    data = {'name': name}
    r = requests.post(f'http://{ip}:{port}/backup/server/', json=data)
    return json.loads(r.text)['content']
  try:
    path = config.basedir + name
    with open(path) as file:
      return file.read()
  except FileNotFoundError:
    return 'El archivo solicitado no existe'

def delete(path, name=None) -> str:
  path = config.basedir + path
  try:
    if name:
      os.remove(path+name)
      return 'Archivo eliminado'
    else:
      shutil.rmtree(path)
      return 'Ruta eliminada'
  except FileNotFoundError:
    return 'Ruta especificada no encontrada'

def delete_all() -> str:
  shutil.rmtree(config.basedir + '/')
  os.mkdir(config.basedir + '/')
  return 'Directorio "Archivos" ha sido reiniciado'

def local_copy(source, dest) -> str:
  source = config.basedir + source
  dest = config.basedir + dest
  if not os.path.exists(source) or not os.path.exists(dest):
    return 'Ruta especificada no existe'
  if not re.fullmatch(config.pathRegex, dest):
    return 'Destino debe ser un directorio'
  newDest = dest + splitPathEnding(source)[1]
  if os.path.exists(newDest):
    return 'Destino ya contiene un archivo/directorio con el mismo nombre'
  try:
    if re.fullmatch(config.pathRegex, source):
      os.makedirs(newDest, exist_ok=True)
      shutil.copytree(source, newDest, dirs_exist_ok=True)
      return 'Ruta copiada exitosamente'
    else:
      shutil.copy(source, dest)
      return 'Ruta copiada exitosamente'
  except shutil.SameFileError:
    return 'Destino no puede ser el mismo directorio'

def copy_to_bucket(source, dest) -> str:
  path_split = splitPathEnding(source)
  local_path = config.basedir + source
  s3 = boto3.resource('s3')
  if os.path.isdir(local_path):
    for dir in os.walk(local_path):
      path = dir[0].removeprefix(local_path)
      key = config.bucket_basedir+dest+path.removeprefix('/')
      if not dir[2]:
        s3.Object(config.bucket_basedir, key).put(Body=b'')
        continue
      for file in dir[2]:
        with open(os.path.join(dir[0], file)) as local_file:
          body = local_file.read()
          cloud.create(path=path_split[0], name=path_split[1], body=body)
    return 'Directorio copiado exitosamente'
  with open(local_path) as local_file:
    body = local_file.read()
    message = cloud.create(path=dest, name=path_split[1], body=body)
    if message == 'El archivo ya existe':
      return 'Archivo con el mismo nombre ya existe en bucket'
  return 'Archivo copiado exitosamente'

def local_transfer(source, dest) -> str:
  source = config.basedir + source
  dest = config.basedir + dest
  if not os.path.exists(source):
    return 'Ruta especificada no existe'
  if not re.fullmatch(config.pathRegex, dest):
    return 'Destino debe ser un directorio'
  if not os.path.exists(dest):
    os.makedirs(dest, exist_ok=True)
    shutil.move(source, dest)
    return 'Ruta transferida exitosamente'
  pathSplit = splitPathEnding(source)
  newDest = dest + pathSplit[1]
  if not os.path.exists(newDest):
    shutil.move(source, dest)
    return 'Ruta transferida exitosamente'
  newDest = renamePath(newDest)
  if pathSplit[2] == 'file':
    with open(newDest, 'x'):
      shutil.copy(source, newDest)
      os.remove(source)
  else:
    os.makedirs(newDest, exist_ok=True)
    shutil.copytree(source, newDest, dirs_exist_ok=True)
    shutil.rmtree(source)
  return 'Ruta renombrada y transferida exitosamente'

def transfer_to_bucket(source, dest) -> str:
  search_key = config.bucket_basedir + dest
  for obj in cloud.bucket.objects.all():
    if obj.key == search_key or search_key in obj.key: break
  else:
    boto3.resource('s3').Object(config.bucket_name, search_key).put(Body=b'')
  copy_to_bucket(source, dest)
  local_path = config.basedir+source
  if os.path.isdir(local_path):
    shutil.rmtree(local_path) 
    return 'Ruta transferida exitosamente'
  os.remove(local_path)
  return 'Ruta transferida exitosamente'

def modify(path:str, body:str) -> str:
  path = config.basedir + path
  if not os.path.exists(path):
    return 'Ruta desconocida'
  try:
    file = open(path,'w')
  except IsADirectoryError:
    return 'Ruta especificada no puede ser un directorio'
  else:
    with file:
      file.write(body)
    return 'Archivo modificado'

def rename(path:str, name:str) -> str:
  path = config.basedir + path
  pathSplit = path.rsplit('/', 1)
  newPath = ''
  if pathSplit[-1] == '':
    newPath = pathSplit[0].rsplit('/',1)[0] + f'/{name.strip("/")}/'
  else:
    newPath = pathSplit[0] + f'/{name}'
  try:
    os.rename(path, newPath)
    return 'Ruta renombrada'
  except FileNotFoundError:
    return 'Ruta desconocida'
  except FileExistsError:
    return 'Ruta especificada ya existe'

def backup_server_files(type_from:str, type_to:str, name, ip=None, port=None) -> str:
  if not(ip and port):
    return backup_to_own_bucket(name)
  if (ip and not port) or (port and not ip):
    raise TypeError
  for dir in os.walk(config.basedir):
    path = dir[0].removeprefix(config.basedir)
    if len(dir[2]) == 0:
      data = {'type': 'dir', 'path': f'/{name}{path}/'}
      requests.post(f'http://{ip}:{port}/backup/{type_to}/', json=data)
      continue
    for file in dir[2]:
      content = open(os.path.join(dir[0],file))
      data = {
        'type': 'file',
        'path': f'/{name}{path}/',
        'name': file,
        'body': content.read()
      }
      content.close()
      requests.post(f'http://{ip}:{port}/backup/{type_to}/', json=data)
  return 'Backup realizado'

def backup_to_own_bucket(name:str) -> str:
  s3 = boto3.resource('s3')
  for dir in os.walk(config.basedir):
    path = dir[0].removeprefix(config.basedir)
    if len(dir[2]) == 0:
      obj = s3.Object(config.bucket_name, f'{name}{path}/')
      obj.put(Body=b'')
      continue
    for file in dir[2]:
      obj = s3.Object(config.bucket_name, f'{name}{path}/{file}')
      with open(os.path.join(dir[0],file), 'rb') as content:
        obj.put(Body=content)
  return 'Backup realizado'

def recover_server_files(type_from:str, type_to:str, name:str, ip=None, port=None) -> str:
  if not(ip and port):
    return recover_to_own_bucket(name)
  if type_to == 'server':
    recover_to_server(type_from, name, ip, port)
  elif type_to == 'bucket':
    cloud.recover_to_bucket(type_from, name, ip, port)
  else:
    raise TypeError
  return f'Recovery desde server externo hacia {type_to} propio'

def recover_to_own_bucket(name:str) -> str:
  cloud.delete_all()
  s3 = boto3.resource('s3')
  dir_path = os.path.join(os.path.join(config.files_dir, name))
  for dir in os.walk(dir_path):
    path = dir[0].removeprefix(dir_path)
    if not dir[2]:
      key = f'{path}/'
      s3.Object(config.bucket_name, key).put(Body=b'')
      continue
    for file in dir[2]:
      key = f'{path}/{file}'
      with open(os.path.join(dir[0], file), 'rb') as content:
        s3.Object(config.bucket_name, key).put(Body=content)
  return 'Recovery desde server propio hacia bucket propio realizado'

def recover_to_server(type_from:str, name:str, ip, port):
  r = requests.post(f'http://{ip}:{port}/recovery/{type_from}/', json={'name': name})
  file_tree = json.loads(r.text)['list']
  delete_all()
  for file in file_tree:
    if file['type'] == 'file':
      create(file['path'], file['name'], file['body'])
    else:
      os.makedirs(file['path'], exist_ok=True)

def send_files_info(name:str) -> list:
  backup_path = config.files_dir+'/'+name
  for dir in os.walk(backup_path):
    file_path = dir[0].removeprefix(backup_path)
    if len(dir[2]) == 0:
      data = {'type': 'dir', 'path':file_path+'/'}
      yield data
      continue
    for file in dir[2]:
      content = open(os.path.join(dir[0], file))
      data = {
        'type': 'file',
        'path':file_path+'/',
        'name': file,
        'body': content.read()
      }
      content.close()
      yield data

def splitPathEnding(path:str) -> list:
  'Devuelve la ruta del archivo y el nombre del archivo por separado'
  if path == '/': return ['/', '', 'dir']
  pathSplit = path.rsplit('/', 1)
  if '.' in pathSplit[1]:
    return [pathSplit[0] + '/', pathSplit[1], 'file']
  where = pathSplit[0].rsplit('/', 1)
  return [where[0] + '/', where[1] + '/', 'dir']

def renamePath(path:str) -> str:
  pathSplit = splitPathEnding(path)
  if pathSplit[2] == 'file':
    fileNameSplit = pathSplit[1].rsplit('.', 1)
    numberSplit = fileNameSplit[0].rsplit('_', 1)
    digit = 1
    if numberSplit[-1].isdigit():
      digit = int(numberSplit[-1]) + 1
    pathSplit[1] = f'{numberSplit[0]}_{digit}.{fileNameSplit[1]}'
  else:
    numberSplit = pathSplit[1].strip('/').rsplit('_', 1)
    digit = 1
    if numberSplit[-1].isdigit():
      digit = int(numberSplit[-1]) + 1
    pathSplit[1] = f'{numberSplit[0]}_{digit}/'
  return pathSplit[0] + pathSplit[1]