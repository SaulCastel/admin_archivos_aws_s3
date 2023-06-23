import unittest
from backend.commands.local import create

class createTest(unittest.TestCase):
  def test_path_is_directory(self):
    kwargs = {
      'path': '/carpeta1/',
      'name': 'carpeta2/',
      'body': 'algo',
      'type': 'server'
    }
    result = create(**kwargs)
    correct = 'Ruta especificada no puede ser un directorio'
    return self.assertEqual(result, correct)

  def test_file_exists(self):
    kwargs = {
      'path': '/carpeta1/',
      'name': 'archivo1.txt',
      'body': 'algo',
      'type': 'server'
    }
    result = create(**kwargs)
    correct = 'Archivo ya existe'
    return self.assertEqual(result, correct)

  def test_create_file(self):
    kwargs = {
      'path': '/carpeta1/',
      'name': 'archivo2.txt',
      'body': 'Contenido archivo 2',
      'type': 'server'
    }
    result = create(**kwargs)
    correct = 'Archivo creado exitosamente'
    return self.assertEqual(result, correct)