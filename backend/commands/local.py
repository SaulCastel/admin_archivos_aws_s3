import os
import shutil
from . import config
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

def localCopy(source, dest) -> str:
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

def localTransfer(source, dest) -> str:
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

def splitPathEnding(path:str) -> list:
  'Devuelve la ruta del archivo y el nombre del archivo por separado'
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