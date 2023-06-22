from .ply.lex import lex, TOKEN
from .ply.yacc import yacc
from re import IGNORECASE

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

tokens = ['ID','PATH','STRING','FILE', 'ARROW'] + list(reserved.values())

literals = ['-']

id = r'([0-9a-z_]+)'

fileRegex = f'({id}[.]{id})'

string = r'("[^"]*")'

path = f'([/]({string}|{fileRegex}|{id}))+[/]?'

t_ignore = ' \t'

@TOKEN(path)
def t_PATH(t):
  t.value = t.value.replace('"','')
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
  localState['message'] = f'Error lexico en: <{t.value}>'
  t.lexer.skip(1)

lexer = lex(reflags=IGNORECASE)

def testLexer(data):
  lexer.input(data)
  for tok in lexer:
    print(tok)

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
  return p[1]

def p_create(p):
  'create : CREATE params'
  pass

def p_delete(p):
  'delete : DELETE params'
  pass 
  
def p_copy(p):
  'copy : COPY params'
  pass

def p_transfer(p):
  'transfer : TRANSFER params'
  pass

def p_rename(p):
  'rename : RENAME params'
  pass

def p_modify(p):
  'modify : MODIFY params'
  pass

def p_backup(p):
  'backup : BACKUP params'
  pass

def p_recovery(p):
  'recovery : RECOVERY params'
  pass

def p_delete_all(p):
  'delete_all : DELETE_ALL params'
  pass

def p_open(p):
  'open : OPEN params'
  pass

def p_params(p):
  'params : params param'
  p[0] = {**p[1], **p[2]}

def p_simgle_param(p):
  'params : param'
  p[0] = p[1]

def p_param(p):
  'param : "-" ID ARROW argument'
  p[0] = {p[2].lower(): p[5]}

def p_argument(p):
  '''argument : ID
              | PATH
              | FILE'''
  p[0] = p[1]

def p_argument_string(p):
  'argument : STRING'
  p[0] = p[1].strip('"')

def p_error(p):
  if not p:
    return 'Comando invalido'
  return f'Error de sintaxis en: <{p.value}>'

parser = yacc()