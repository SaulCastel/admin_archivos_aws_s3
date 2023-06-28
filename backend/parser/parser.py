from .ply.lex import lex, TOKEN
from .ply.yacc import yacc
from re import IGNORECASE
import backend.commands.local as local
import backend.commands.cloud as cloud

reserved = {
  'create': 'CREATE',
  'delete': 'DELETE',
  'copy': 'COPY',
  'transfer': 'TRANSFER',
  'rename': 'RENAME',
  'modify': 'MODIFY',
  'backup': 'BACKUP',
  'recovery': 'RECOVERY',
  'delete_all': 'DELETE_ALL',
  'open': 'OPEN'
}

tokens = ['ID','PATH','STRING','FILE', 'ARROW', 'IP'] + list(reserved.values())

literals = ['-']

id = r'([0-9a-z_\[\]\(\)]+)'

fileRegex = f'({id}[.]{id})'

string = r'("[^"]*")'

path = f'([/]({string}|{fileRegex}|{id})?)+'

t_ignore = ' \t'

@TOKEN(path)
def t_PATH(t):
  t.value = t.value.replace('"','')
  return t

def t_IP(t):
  '([0-9]{0,3}\.)+[0-9]{0,3}'
  return t

@TOKEN(fileRegex)
def t_FILE(t):
  return t

@TOKEN(id)
def t_ID(t):
  t.type = reserved.get(t.value.lower(),'ID')
  return t

@TOKEN(string)
def t_STRING(t):
  return t

def t_ARROW(t):
  '->'
  return t

def t_newline(t):
  r'[\r\n]'
  t.lexer.lineno += 1

def t_error(t):
  print(f'Error lexico en: <{t.value}>')
  t.lexer.skip(1)

lexer = lex(reflags=IGNORECASE)

def testLexer(data):
  lexer.input(data)
  for tok in lexer:
    print(tok)

def exec_simple_type_command(local, cloud, params:dict) -> str:
  '''
  Verifica que el parametro "type" exista y ejecuta
  el comando correspondiente al tipo de operacion.
  '''
  try:
    type = params.pop('type')
  except KeyError:
    return 'Especificacion invalida de tipo'
  else:
    try:
      if type == 'server':
        return local(**params)
      else:
        return cloud(**params)
    except TypeError:
      return 'Parametro(s) invalido(s)'

def exec_double_type_command(commands:dict, params:dict) -> str:
  try:
    type_from = params.pop('type_from')
    type_to = params.pop('type_to')
    params['source'] = params.pop('from')
    params['dest'] = params.pop('to')
  except KeyError:
    return 'Especificacion invalida de tipo'
  else:
    try:
      if type_from == 'server' and type_to == 'server':
        return commands['server-server'](**params)
      elif type_from == 'server' and type_to == 'bucket':
        return commands['server-bucket'](**params)
      elif type_from == 'bucket' and type_to == 'server':
        return commands['bucket-server'](**params)
      else:
        return commands['bucket-bucket'](**params)
    except TypeError:
      return 'Parametro(s) invalido(s)'

def exec_api_command(commands:dict, params) -> str:
  try:
    type_from = params.pop('type_from')
    type_to = params.pop('type_to')
  except KeyError:
    return 'Especificacion invalida de tipo'
  else:
    ip = params.get('ip')
    port = params.get('port')
    try:
      if type_from == 'server' and type_to == 'server':
        if not(ip and port):
          return 'Se necesita ip y puerto para operacion con tipos iguales'
        return commands['server-server']('server', **params)
      if type_from == 'bucket' and type_to == 'bucket':
        if not(ip and port):
          return 'Se necesita ip y puerto para operacion con tipos iguales'
        return commands['bucket-bucket']('bucket', **params)
      elif type_from == 'server' and type_to == 'bucket':
        return commands['server-bucket']('bucket',**params)
      else:
        return commands['bucket-server']('server', **params)
    except TypeError:
      return 'Parametro(s) invalido(s)'

def p_command(p):
  '''command  : create
              | delete
              | copy
              | transfer
              | rename
              | modify
              | backup
              | recovery
              | delete_all
              | open'''
  p[0] = p[1]

def p_create(p):
  'create : CREATE params'
  p[0] = exec_simple_type_command(local.create, cloud.create, p[2])

def p_delete(p):
  'delete : DELETE params'
  p[0] = exec_simple_type_command(local.delete, cloud.delete, p[2])
  
def p_copy(p):
  'copy : COPY params'
  commands = {
    'server-server': local.local_copy,
    'server-bucket': local.copy_to_bucket,
    'bucket-server': cloud.copy_to_server,
    'bucket-bucket': cloud.cloud_copy
  }
  p[0] = exec_double_type_command(commands, p[2])

def p_transfer(p):
  'transfer : TRANSFER params'
  commands = {
    'server-server': local.local_transfer,
    'server-bucket': local.transfer_to_bucket,
    'bucket-server': cloud.transfer_to_server,
    'bucket-bucket': cloud.cloud_transfer
  }
  p[0] = exec_double_type_command(commands, p[2])

def p_rename(p):
  'rename : RENAME params'
  p[0] = exec_simple_type_command(local.rename, cloud.rename, p[2])

def p_modify(p):
  'modify : MODIFY params'
  p[0] = exec_simple_type_command(local.modify, cloud.modify, p[2])

def p_backup(p):
  'backup : BACKUP params'
  commands = {
    'server-server': local.backup_server_files,
    'server-bucket': local.backup_server_files,
    'bucket-server': cloud.backup_bucket_files,
    'bucket-bucket': cloud.backup_bucket_files
  }
  p[0] = exec_api_command(commands, p[2])

def p_recovery(p):
  'recovery : RECOVERY params'
  pass

def p_delete_all(p):
  'delete_all : DELETE_ALL params'
  p[0] = exec_simple_type_command(local.delete_all, cloud.delete_all, p[2])

def p_open(p):
  'open : OPEN params'
  p[0] = exec_simple_type_command(local.open_file, cloud.open_file, p[2])

def p_params(p):
  'params : params param'
  p[0] = {**p[1], **p[2]}

def p_simgle_param(p):
  'params : param'
  p[0] = p[1]

def p_param(p):
  'param : "-" ID ARROW argument'
  p[0] = {p[2].lower(): p[4]}

def p_argument(p):
  '''argument : ID
              | PATH
              | FILE
              | IP'''
  p[0] = p[1]

def p_argument_string(p):
  'argument : STRING'
  p[0] = p[1].strip('"')

def p_error(p):
  if not p:
    print('Comando invalido')
    return
  print(f'Error de sintaxis en: <{p.value}>')

parser = yacc()