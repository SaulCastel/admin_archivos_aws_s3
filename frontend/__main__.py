from os import makedirs, path
import frontend.AES_ECB as AES
import frontend.Login
from backend.commands import config

users = {}
makedirs(config.basedir, exist_ok=True)
try:
  usersFile = open(config.files_dir+'/miausuarios.txt', 'r')
except FileNotFoundError:
  print('No se encuentra un archivo con usuarios. Terminando aplicación...')
else:
  with usersFile:
    while True:
      user = usersFile.readline().strip()
      if not user:
        break
      password = usersFile.readline().strip()
      password = AES.decryptFromHex(b'miaproyecto12345',password)
      users[user] = password
    frontend.Login.Login(users)