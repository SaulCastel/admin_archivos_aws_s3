import unittest
from backend.commands.local import localTransfer

class TestLocalTransfer(unittest.TestCase):
  def test_file_moved(self):
    kwargs = {
      'source': '/carpeta1/archivo1.txt',
      'dest': '/carpeta3/'
    }
    result = localTransfer(**kwargs)
    correct = 'Ruta transferida exitosamente'
    return self.assertEqual(result, correct)

  def test_dir_moved(self):
    kwargs = {
      'source': '/carpeta2/',
      'dest': '/carpeta3/'
    }
    result = localTransfer(**kwargs)
    correct = 'Ruta transferida exitosamente'
    return self.assertEqual(result, correct)

  def test_file_renamed(self):
    kwargs = {
      'source': '/carpeta1/archivo2.txt',
      'dest': '/'
    }
    result = localTransfer(**kwargs)
    correct = 'Ruta renombrada y transferida exitosamente'
    return self.assertEqual(result, correct)

  def test_dir_renamed(self):
    kwargs = {
      'source': '/carpeta1/existe/',
      'dest': '/'
    }
    result = localTransfer(**kwargs)
    correct = 'Ruta renombrada y transferida exitosamente'
    return self.assertEqual(result, correct)

  def test_file_not_found(self):
    kwargs = {
      'source': '/carpeta1/noexiste.txt',
      'dest': '/carpeta3/'
    }
    result = localTransfer(**kwargs)
    correct = 'Ruta especificada no existe'
    return self.assertEqual(result, correct)

  def test_dest_not_dir(self):
    kwargs = {
      'source': '/carpeta1/archivo3.txt',
      'dest': '/carpeta3/archivo1.txt'
    }
    result = localTransfer(**kwargs)
    correct = 'Destino debe ser un directorio'
    return self.assertEqual(result, correct)