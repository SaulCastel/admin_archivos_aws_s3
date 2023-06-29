import os

files_dir = os.path.expanduser('~/files_proy2')
dir ='~/files_proy2/'
basedir = files_dir + "/Archivos"
bucket_name = '201801178'
bucket_basedir = 'Archivos'
ip = '52.90.79.49'
port = '8000'
server_url = f'http://{ip}:{port}'

pathRegex = '([/]([0-9a-zA-Z_ \[\]\(\)-]+)?)+'