from os import makedirs, path
import frontend.AES_ECB as AES
import frontend.Login
from backend.commands.cloud import get_users_file

users = {}
data = get_users_file()
if not data:
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