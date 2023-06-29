import io
import os
from urllib import request
import boto3
import requests
import json
from config import bucket_name, bucket_basedir, dir, basedir

s3 = boto3.resource('s3')
bucket = s3.Bucket(bucket_name)

def create(path:str, name:str, body:str) -> str:
  key = bucket_basedir+path+name
  for obj in bucket.objects.all():
    if key == obj.key:
      return 'El archivo ya existe'
  object = s3.Object(bucket_name, key)
  object.put(Body=body.encode())
  return 'Archivo creado exitosamente'

def delete(path, name=None) -> str:
  for obj in bucket.objects.all():
    objeto = bucket_basedir+path+name
    if objeto == obj.key:
      s3.Object(bucket_name, objeto).delete()
      separar = (bucket_basedir+path).split('/')
      separar.pop()
      path="/".join(separar)
      new_path = path + "/"+name
      object = s3.Object(bucket_name, new_path)
      body = ""
      object.put(Body=body.encode())
      return 'Eliminado Exitosamente'
  return 'El archivo y/o Carpeta no Existe'

def modify(path:str, body:str) -> str:
  for obj in bucket.objects.all():
    objeto = bucket_basedir+path
    if objeto == obj.key:
      s3Object = s3.Object(bucket_name, key=(objeto))
      s3Object.put(Body=body.encode())
      return 'Modificado Exitosamente'
  return 'El archivo y/o Carpeta no Existe'

def renombrar(path:str, new_name:str) -> str:
  old_name = s3.object(bucket_name, path)
  new = s3.object(bucket_name, new_name)
  new.copy_from(
      CopySource=f'{bucket_name}/{old_name}'
  )
  old_name.delete()

def rename(path:str, name:str) -> str:
  path1 = bucket_basedir+path
  new_name = ''
  for obj in bucket.objects.all():
    if path1 == obj.key:
      separar = (path1).split('/')
      separar.pop()
      path="/".join(separar)
      new_name = path + "/"+name
      break
  renombrar(bucket_name, path, new_name)
  return 'Renombrado Exitosamente'

def delete_all() -> str:
  for obj in bucket.objects.all():
    if obj.key == 'miausuarios.txt':
      continue
    s3.Object(bucket_name, obj.key).delete()
  object = s3.Object(bucket_name, bucket_basedir+'/vacio.txt')
  object.put(Body=''.encode())
  return 'Bucket Vacio Completamente'

  
def cloud_copy(source, dest) -> str:
  source1 = bucket_basedir+source
  dest1 = bucket_basedir+dest
  if source1.endswith(".txt"):
    obtener = source1.split("/")
    name = dest1+obtener[len(obtener)-1]
    try:
      objeto_origen = {
        'Bucket': bucket_name,
        'Key': source
      }
        
      objeto_destino = {
        'Bucket': bucket_name,
        'Key': name
      }

      s3.Object(objeto_destino['Bucket'], objeto_destino['Key']).copy(objeto_origen)
      return ("Archivo Copiado exitosamente")
    except Exception as e:
            return("Error al copiar el archivo:", str(e))
  else:
        obtener = source.split("/")
        obtener.pop()
        name = dest+obtener[len(obtener)-1]+"/"
        try:
            for objeto in bucket.objects.filter(Prefix=source):
                destino_objeto = objeto.key.replace(source, name, 1)
                bucket.Object(destino_objeto).copy_from(CopySource={'Bucket': bucket_name, 'Key': objeto.key})
                print(f"Objeto copiado exitosamente: {destino_objeto}")
            return("Carpeta Copiada exitosamente")
        except Exception as e:
            return ("Error al copiar la carpeta:", str(e))                       

def copy_to_server(source, dest) -> str:
  source1 = bucket_basedir+source
  dest1 = bucket_basedir+dest
  try:
        for objeto in bucket.objects.filter(Prefix=source1):
            # Obtener el nombre del objeto sin la ruta completa
            if source.endswith(".txt"):
                nombre_objeto = os.path.basename(objeto.key)
                destino = dest1
                ruta_destino = os.path.join(destino, nombre_objeto)
                os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
                # Descargar el objeto desde S3 a la ruta local
                bucket.download_file(objeto.key, ruta_destino)
                print(f"Objeto transferido exitosamente: {ruta_destino}")
            else:
                return "No se pudo implementar en carpetas"

        return ("Copia completada exitosamente")
  except Exception as e:
        return ("Error al transferir los objetos:", str(e))

def cloud_transfer(source, dest) -> str:
  source1 = bucket_basedir+source
  dest1 = bucket_basedir+dest
  if source1.endswith(".txt"):
    obtener = source1.split("/")
    name = dest1+obtener[len(obtener)-1]
    reponer = "/".join(obtener[:-1]) + "/"
    print(reponer)
    try:
      objeto_origen = {
        'Bucket': bucket_name,
        'Key': source
      }
      objeto_destino = {
        'Bucket': bucket_name,
        'Key': name
      }
      s3.Object(objeto_destino['Bucket'], objeto_destino['Key']).copy(objeto_origen)
      print("Archivo Transferido exitosamente")
      eliminar =s3.Object(objeto_origen['Bucket'],objeto_origen['Key'])
      eliminar.delete()
      create = s3.Object(bucket_name, reponer)
      create.put(Body="".encode())
    except Exception as e:
      print("Error al copiar el archivo:", str(e))
  else:
      obtener = source.split("/")
      obtener.pop()
      name = dest+obtener[len(obtener)-1]+"/"
      reponer = "/".join(obtener[:-1]) + "/"
      print(reponer)
      try:
        for objeto in bucket.objects.filter(Prefix=source):
          destino_objeto = objeto.key.replace(source, name, 1)
          bucket.Object(destino_objeto).copy_from(CopySource={'Bucket': bucket_name, 'Key': objeto.key})
          eliminar =s3.Object(bucket_name,objeto.key)
          eliminar.delete()
          print(f"Objeto Transferido exitosamente: {destino_objeto}")
        print("Carpeta Transferida exitosamente")
        create = s3.Object(bucket_name, reponer)
        create.put(Body="".encode())
      except Exception as e:
        print("Error al copiar la carpeta:", str(e))

def transfer_to_server(source, dest) -> str:
  return 'Falta implementar este comando'

def backup_bucket_files(type_to:str, name, ip=None, port=None) -> str:
  if not(ip and port):
    return backup_to_own_server(name)
  for objeto in bucket.objects.filter(Prefix='Archivos/'):
    data = {}
    if objeto.key.endswith(".txt"):
      separar = objeto.key.split("/")
      separar[0] = name
      s3_object = s3.Object(bucket_name, objeto.key)
      with io.BytesIO() as f:
        s3_object.download_fileobj(f)
        f.seek(0)
        data = {
          'type' : 'file',
          'path' : '/'+"/".join(separar[:-1])+"/",
          'name' : separar[len(separar)-1],
          'body' : f.read().decode()
        }
    else:
      path = objeto.key.removeprefix('Archivos')
      data = {
        'type': 'dir',
        'path': f'{name}{path}'
      }
    requests.post(f'http://{ip}:{port}/backup/{type_to}/', json = data)
  return 'Backup de Bucket Realizado'

def backup_to_own_server(name:str) -> str:
  try:
    for objeto in bucket.objects.filter(Prefix="Archivos/"):
      separar =  objeto.key.split("/")
      separar[0]=name
      ruta_objeto ="/".join(separar)
      ruta_local = os.path.join("Archivos/", ruta_objeto)
      ruta_local =ruta_local.replace("\\","/")
      # Crear el directorio local si no existe
      os.makedirs(os.path.dirname(ruta_local), exist_ok=True)
      # Descargar el objeto desde S3 al directorio local
      bucket.download_file(objeto.key, ruta_local)
      return (f"Objeto descargado exitosamente: {ruta_local}")
    return ("Descarga del bucket completada exitosamente")
  except Exception as e:
    return ("Error al descargar el bucket:", str(e))


def open_file(name, ip=None, port=None) -> str:
  if ip and port:
    data = {'name': name}
    r = requests.post(f'http://{ip}:{port}/open/bucket/', json=data)
    return json.loads(r.text)['content']
  for obj in bucket.objects.all():
    if obj.key == name:
      data = obj.get()['Body'].read()
      return data.decode()
  return 'Ruta desconocida'