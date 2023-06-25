import boto3
from . import config

def create(path:str, name:str, body:str) -> str:
  s3 = boto3.resource('s3')
  key = config.bucket_basedir + path + name
  object = s3.Object(config.bucket_name, key)
  object.put(Body=body.encode())
  return 'Archivo creado exitosamente'

def delete(path, name=None) -> str:
  return 'Falta implementar este comando'

def modify(path:str, body:str) -> str:
  return 'Falta implementar este comando'

def rename(path:str, name:str) -> str:
  return 'Falta implementar este comando'

def delete_all() -> str:
  return 'Falta implementar este comando'

def cloud_copy(source, dest) -> str:
  return 'Falta implementar este comando'

def copy_to_server(source, dest) -> str:
  return 'Falta implementar este comando'

def cloud_transfer(source, dest) -> str:
  return 'Falta implementar este comando'

def transfer_to_server(source, dest) -> str:
  return 'Falta implementar este comando'