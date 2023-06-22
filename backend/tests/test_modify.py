import unittest
from backend.commands.local import modify

class modifyTest(unittest.TestCase):
  def test_file_doesnt_exist(self):
    kwargs = {
      'path': '/carpeta1/archivo2.txt',
      'body': 'Este es un texto nuevo',
      'type': 'server'
    }
    result = modify(**kwargs)
    correct = 'Ruta desconocida'
    return self.assertEqual(result, correct)

  def test_is_directory(self):
    kwargs = {
      'path': '/carpeta1/',
      'body': 'Este es un texto nuevo',
      'type': 'server'
    }
    result = modify(**kwargs)
    correct = 'Ruta especificada no puede ser un directorio'
    return self.assertEqual(result, correct)

  def test_modify_file(self):
    kwargs = {
      'path': '/carpeta1/archivo1.txt',
      'body': 'Este es un texto nuevo',
      'type': 'server'
    }
    result = modify(**kwargs)
    correct = 'Archivo modificado'
    return self.assertEqual(result, correct)