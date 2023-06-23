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

def localCopy(source, dest) -> str:
  source = config.basedir + source
  dest = config.basedir + dest
  if not os.path.exists(source) or not os.path.exists(dest):
    return 'Ruta especificada no existe'
  if not re.fullmatch(config.pathRegex, dest):
    return 'Destino debe ser un directorio'
  newDest = dest + splitPathEnding(source)[1]
  if os.path.exists(newDest):
    return 'La ruta especificada ya existe'
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

def transfer(source, dest, type_to, type_from) -> str:
  src = config.basedir + source
  dst = config.basedir + dest
  if not re.fullmatch(config.pathRegex, dest):
    return 'Ruta destino debe ser un directorio'
  os.makedirs(dst, exist_ok=True)
  try:
    shutil.move(src, dst)
    return 'Ruta transferida exitosamente'
  except FileNotFoundError:
    return 'Ruta desconocida'
  except shutil.Error:
    renamed = renamePath(source)
    dir = config.basedir + renamed[0]
    os.makedirs(dir,exist_ok=True)
    if not re.fullmatch(config.pathRegex, source):
      with open(dir+renamed[1],'w') as file:
        file.write('')
    copy(dir, dir+renamed[1])
    if re.fullmatch(config.pathRegex, source):
      shutil.rmtree(dir)
    else:
      os.remove(dir+renamed[1])
    return 'Ruta transferida y renombrada'

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

def splitPathEnding(path:str) -> tuple:
  'Devuelve la ruta del archivo y el nombre del archivo por separado'
  pathSplit = path.rsplit('/', 1)
  if '.' in pathSplit[1]:
    return (pathSplit[0] + '/', pathSplit[1])
  where = pathSplit[0].rsplit('/', 1)
  return (where[0] + '/', where[1] + '/')

def renamePath(path:str) -> tuple:
  pathSplit = path.strip('/').split('/')
  if '.' in pathSplit[-1]:
    fileSplit = pathSplit[-1].split('.')
    numberSplit = fileSplit[0].rsplit('_', 1)
    digit = '1'
    if numberSplit[-1].isdigit():
      digit = int(numberSplit[-1]) + 1
    pathSplit[-1] = numberSplit[0] + f'_{digit}.{fileSplit[1]}'
    return buildPath(pathSplit)
  else:
    numberSplit = pathSplit[-1].split('_', 1)
    digit = '1'
    if numberSplit[-1].isdigit():
      digit = int(numberSplit[-1]) + 1
    pathSplit[-1] = numberSplit[0] + f'_{digit}'
    return buildPath(pathSplit)

def buildPath(tree: list) -> tuple:
  path = ''
  for i in range(len(tree)-1):
    path += f'/{tree[i]}'
  path += '/'
  return (path, tree[-1])