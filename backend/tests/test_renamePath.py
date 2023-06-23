import unittest
from backend.commands.local import renamePath

class TestRenamePath(unittest.TestCase):
  def test_renameFile(self):
    path = '/archivo2.txt'
    result = renamePath(path)
    correct = '/archivo2_1.txt'
    return self.assertEqual(result, correct)

  def test_renameDir(self):
    path = '/existe/'
    result = renamePath(path)
    correct = '/existe_1/'
    return self.assertEqual(result, correct)

if __name__ == '__main__':
  unittest.main()