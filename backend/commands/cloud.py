import boto3
from . import config
s3 = boto3.resource('s3')
bucket_name = config.bucket_name
bucket = s3.Bucket(config.bu)
def create(path:str, name:str, body:str) -> str:
  key = config.bucket_basedir + path + name
  object = s3.Object(bucket_name, key)
  object.put(Body=body.encode())
  return 'Archivo creado exitosamente'

def delete(path, name=None) -> str:
  for obj in bucket.objects.all():
    objeto = config.bucket_basedir+path+name
    if objeto == obj.key:
      s3.Object(bucket_name, objeto).delete()
      return 'Eliminado Exitosamente'
    else:
      return 'El archivo y/o Carpeta no Existe'

  

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