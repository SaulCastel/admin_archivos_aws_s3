import unittest
from backend.commands.local import localCopy, splitPathEnding

class testLocalCopy(unittest.TestCase):
  def test_localCopy_file(self):
    kwargs = {
      'source': '/carpeta1/archivo1.txt',
      'dest': '/'
    }
    result = localCopy(**kwargs)
    correct = 'Ruta copiada exitosamente'
    return self.assertEqual(result, correct)

  def test_localCopy_dir(self):
    kwargs = {
      'source': '/carpeta1/',
      'dest': '/carpeta2/'
    }
    result = localCopy(**kwargs)
    correct = 'Ruta copiada exitosamente'
    return self.assertEqual(result, correct)
  
  def test_localCopy_file_exists(self):
    kwargs = {
      'source': '/carpeta1/archivo1.txt',
      'dest': '/carpeta2/'
    }
    print(splitPathEnding('/carpeta1/archivo1.txt'))
    result = localCopy(**kwargs)
    correct = 'La ruta especificada ya existe'
    return self.assertEqual(result, correct)

  def test_localCopy_dir_exists(self):
    kwargs = {
      'source': '/carpeta1/',
      'dest': '/carpeta2/'
    }
    result = localCopy(**kwargs)
    correct = 'La ruta especificada ya existe'
    return self.assertEqual(result, correct)

  def test_localCopy_file_doesnt_exist(self):
    kwargs = {
      'source': '/carpeta1/archivo3.txt',
      'dest': '/'
    }
    result = localCopy(**kwargs)
    correct = 'Ruta especificada no existe'
    return self.assertEqual(result, correct)

  def test_localCopy_dir_doesnt_exist(self):
    kwargs = {
      'source': '/carpeta1/',
      'dest': '/carpeta3/'
    }
    result = localCopy(**kwargs)
    correct = 'Ruta especificada no existe'
    return self.assertEqual(result, correct)

  def test_localCopy_dest_not_directory(self):
    kwargs = {
      'source': '/carpeta1/',
      'dest': '/carpeta2/archivo1.txt'
    }
    result = localCopy(**kwargs)
    correct = 'Destino debe ser un directorio'
    return self.assertEqual(result, correct)

  def test_localCopy_sameFileError(self):
    kwargs = {
      'source': '/carpeta1/',
      'dest': '/'
    }
    result = localCopy(**kwargs)
    correct = 'Destino no puede ser el mismo directorio'
    return self.assertEqual(result, correct)