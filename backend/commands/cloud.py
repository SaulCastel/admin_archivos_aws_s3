import io
import os
import boto3
import botocore.errorfactory
from config import bucket_name, bucket_basedir, dir

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
  #Para Carpetas y archivos
  for obj in bucket.objects.all():
    if (source1 in obj.key) or (source1 == obj.key):
        for obj in bucket.objects.filter(Prefix = source1):
            if not os.path.exists(os.path.expanduser(dir+dest)):
                print(os.path.expanduser(obj.key))
                os.makedirs(os.path.expanduser(obj.key))
            bucket.download_file(obj.key, obj.key)
            return 'Copia Realizada con Exito'
    else:
       return "No se puede realizar la copia, la carpeta y/o archivo no existe"
    

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

def open_file(name) -> str:
  try:
    obj = s3.Object(bucket_name, key=name).get()
    data = obj['Body'].read()
    return data.decode()
  except:
    return 'Ruta desconocida'