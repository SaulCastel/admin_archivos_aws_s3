from os import makedirs, path
import frontend.AES_ECB as AES
import frontend.Login
import frontend.Comando
from backend.commands.cloud import open_file

'''
users = {}
data = open_file('miausuarios.txt')
if data == 'Ruta desconocida':
  print('No se encuentra un archivo con usuarios. Terminando aplicación...')
else:
  entries = data.split('\n')
  index = 0
  while index < len(entries):
    user = entries[index].strip()
    index += 1
    password = entries[index].strip()
    index += 1
    password = AES.decryptFromHex(b'miaproyecto12345',password)
    users[user] = password
  print(users)
  frontend.Login.Login(users)
'''
app = frontend.Comando.Comandos()
app.run()