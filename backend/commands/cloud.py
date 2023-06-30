import io
import os
import shutil
from urllib import request
import boto3
import requests
import json
from config import bucket_name, bucket_basedir, files_dir, basedir
import backend.commands.local as local

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

def rename(path:str, name:str) -> str:
  path1 = bucket_basedir+path
  try:
    objeto = s3.Object(bucket_name, path1)
    ruta_destino = objeto.key.rsplit('/', 1)[0] + '/' + name
    s3.Object(bucket_name, ruta_destino).copy_from(CopySource={'Bucket': bucket_name, 'Key': objeto.key})
    objeto.delete()
    return f"Objeto renombrado exitosamente. Nuevo nombre: {ruta_destino}"
  except Exception as e:
    return "Error al renombrar el objeto:" + str(e)

def delete_all() -> str:
  for obj in bucket.objects.filter(Prefix=bucket_basedir):
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
      return "Archivo Copiado exitosamente"
    except Exception as e:
            return "Error al copiar el archivo:"+ str(e)
  else:
        obtener = source.split("/")
        obtener.pop()
        name = dest+obtener[len(obtener)-1]+"/"
        try:
            for objeto in bucket.objects.filter(Prefix=source):
                destino_objeto = objeto.key.replace(source, name, 1)
                bucket.Object(destino_objeto).copy_from(CopySource={'Bucket': bucket_name, 'Key': objeto.key})
                print(f"Objeto copiado exitosamente: {destino_objeto}")
            return "Carpeta Copiada exitosamente"
        except Exception as e:
            return "Error al copiar la carpeta:" + str(e)                     

def copy_to_server(source, dest) -> str:
  source1 = bucket_basedir+source
  dest1 = files_dir+dest
  try:
        for objeto in bucket.objects.filter(Prefix=source1):
            # Obtener el nombre del objeto sin la ruta completa
            if source1.endswith(".txt"):
                nombre_objeto = os.path.basename(objeto.key)
                ruta_destino = os.path.join(dest1, nombre_objeto)
                os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
                # Descargar el objeto desde S3 a la ruta local
                bucket.download_file(objeto.key, ruta_destino)
                print(f"Objeto copiado exitosamente: {ruta_destino}")
            else:
                return "No se pudo implementar en carpetas"

        return "Copia completada exitosamente"
  except Exception as e:
        return "Error al copiar los objetos:"+ str(e)

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
      return "Error al copiar el archivo:" + str(e)
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
        return "Carpeta Transferida exitosamente"
        create = s3.Object(bucket_name, reponer)
        create.put(Body="".encode())
      except Exception as e:
        return "Error al copiar la carpeta:"+ str(e)

def transfer_to_server(source, dest) -> str:
  source1 = bucket_basedir+source
  dest1 = files_dir+dest
  try:
        for objeto in bucket.objects.filter(Prefix=source1):
            if source1.endswith(".txt"):
                nombre_objeto = os.path.basename(objeto.key)
                ruta_destino = os.path.join(dest1, nombre_objeto)
                os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
                bucket.download_file(objeto.key, ruta_destino)
                print(f"Objeto copiado exitosamente: {ruta_destino}")
                eliminar = s3.Object(bucket_name, objeto.key)
                eliminar.delete()
            else:
                return "No se pudo implementar en carpetas"

        return "Transferencia completada exitosamente"
  except Exception as e:
        return "Error al Transferir los objetos:"+ str(e)

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
      ruta_local = os.path.join(files_dir, ruta_objeto)
      ruta_local =ruta_local.replace("\\","/")
      os.makedirs(os.path.dirname(ruta_local), exist_ok=True)
      bucket.download_file(objeto.key, ruta_local)
    return "Descarga del bucket completada exitosamente"
  except Exception as e:
    return "Error al descargar el bucket:" + str(e)

def recover_bucket_files(type_to:str, name:str, ip=None, port=None) -> str:
  if not(ip and port):
    return recover_to_own_server(name)
  if type_to == 'server':
    local.recover_to_server(name, ip, port)
  elif type_to == 'bucket':
    recover_to_bucket(name, ip, port)
  else:
    raise TypeError
  return f'Recovery desde bucket externo hacia {type_to} propio'

def recover_to_own_server(name:str) -> str:
  shutil.rmtree(basedir + '/')
  os.mkdir(basedir + '/')
  try:
    for objeto in bucket.objects.filter(Prefix=name):
        if objeto.key.endswith(".txt"):
            nombre_objeto = objeto.key.removeprefix(name)
            ruta_destino = os.path.dirname(basedir)+nombre_objeto
            ruta_destino =ruta_destino.replace('\\','/')
            os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
            bucket.download_file(objeto.key, ruta_destino)
        else:
            nombre_objeto = os.path.basename(objeto.key)
            ruta_destino = os.path.join(os.path.dirname('Archivos/'), nombre_objeto)
            ruta_destino =ruta_destino.replace('\\','/')
            if not os.path.exists(ruta_destino):
                os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
                bucket.download_file(objeto.key, ruta_destino)
    return "Descarga del recovery completada exitosamente"
  except Exception as e:
    return "Error al descargar el recovery:" + str(e)

def recover_to_bucket(name:str, ip, port):
  r = requests.post(f'http://{ip}:{port}/recovery/server/', json={'name': name})
  files = json.loads(r.text)['list']
  delete_all()
  for file in files:
    file_lista = file['path'].removeprefix(name)
    file['path'] = f'Archivos/{file_lista}' 
    if file['type'] == 'file':
      create(file['path'], file['name'], file['body'])
    else:
      create(file['path'], file['name'],"")
  return "Recovery Realizado"

def get_users_file():
  for obj in bucket.objects.all():
    if obj.key == 'miausuarios.txt':
      data = obj.get()['Body'].read()
      return data.decode()

def open_file(name, ip=None, port=None) -> str:
  if ip and port:
    data = {'name': name}
    r = requests.post(f'http://{ip}:{port}/open/bucket/', json=data)
    return json.loads(r.text)['content']
  for obj in bucket.objects.filter(Prefix=bucket_basedir):
    name = bucket_basedir + name
    if obj.key == name:
      data = obj.get()['Body'].read()
      return data.decode()
  return 'Ruta desconocida'