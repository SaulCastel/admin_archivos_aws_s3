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
  for obj in bucket.objects.all():
    objeto = config.bucket_basedir+path
    if objeto == obj.key:
      s3Object = s3.Object(bucket_name, key=(objeto))
      s3Object.put(Body=body.encode())
      return 'Modificado Exitosamente'
    else:
      return 'El archivo y/o Carpeta no Existe'
  

def renombrar(path:str, new_name:str) -> str:
    old_name = s3.object(bucket_name, path)
    new = s3.object(bucket_name, new_name)
    new.copy_from(
       CopySource=f'{bucket_name}/{old_name}'
    )
    old_name.delete()

def rename(path:str, name:str) -> str:
  for obj in bucket.objects.all():
    if path == obj.key:
        separar = config.bucket_basedir+path.split('/')
        separar.pop()
        path="/".join(separar)
        new_name = path + "/"+name
        if new_name == obj.key:
            return "El Archivo ya existe, no se puede utilizar este nombre"
        else:
            renombrar(bucket_name, path, new_name)
            return 'Renombrado Exitosamente'

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