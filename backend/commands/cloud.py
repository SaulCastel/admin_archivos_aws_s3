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

def copiar(path:str, new_name:str) -> str:
  old_name = s3.object(bucket_name, path)
  new = s3.object(bucket_name, new_name)
  new.copy_from(
      CopySource=f'{bucket_name}/{old_name}'
  )
  
def cloud_copy(source, dest) -> str:
  source1 = bucket_basedir+source
  dest1 = bucket_basedir+dest
  #Copy Archivos
  for obj in bucket.objects.all():
    if source1 == obj.key:
        separar = source1.split('/')
        if separar[len(separar)-1].endswith(".txt")==True:
            destino = dest1 + separar[len(separar)-1]
            for obj1 in bucket.objects.all():
                if destino == obj1.key:
                    s = destino.split("/")
                    r=s[len(s)-1].split(".")
                    cambio = r[0]+ "(copy)."+r[1]
                    destinoFinal = dest1 + cambio
                    copiar(bucket_name, source1, destinoFinal)
                    print("El Archivo ya existe, Se añadio copy al nombre")
                    break
                else:
                    copiar(bucket_name, source1, destino)
    #Copy Carpetas
    else:
        buscar = source1.split("/")
        buscar.pop()
        if source1 in obj.key:
            separar2 = obj.key.split("/") #Carpeta de donde se encuentra en el bucket
            separar = dest1.split("/") #Carpeta Destino
            separar.pop()
            #Obteniendo para crear
            if buscar[len(buscar)-1] in dest1:
                print("La carpeta ya Existe")
            
            else:
                for y in range(0,len(separar2)):
                    if buscar[len(buscar)-1] == separar2[y]:
                        new_list = separar2[y:]
                        separar.extend(new_list)
                        unir = "/".join(separar)
                        s3_object = s3.Object(bucket_name, obj.key)
                        with io.BytesIO() as f:
                            s3_object.download_fileobj(f)
                            f.seek(0)
                            Body = f.read()
                            object = s3.Object(bucket_name, unir)
                            object.put(Body=Body)
                            for obj2 in bucket.objects.all(): 
                               if unir == obj2.key:
                                  u = unir.split("/")
                                  p = u[len(s)-1].split(".")
                                  renombre = p[0]+ "(copy)."+p[1]
                                  u[len(s)-1] = renombre
                                  unir = "/".join(u)
                                  copiar(bucket_name, obj.key, unir)
                               else:
                                  copiar(bucket_name, obj.key, unir)                              
  return 'El archivo y/o Carpeta no Existe'

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
  return 'Falta implementar este comando'

def transfer_to_server(source, dest) -> str:
  return 'Falta implementar este comando'

def open_file(name) -> str:
  try:
    obj = s3.Object(bucket_name, key=name).get()
    data = obj['Body'].read()
    return data.decode()
  except:
    return 'Ruta desconocida'