import unittest
import backend.parser.parser as parser

class parser_test(unittest.TestCase):
  def test_tokenizer(self):
    command = 'OpEn -param1->VAluE1 -ParaM2->"Value 2" -paRam_3->/"Value 3_1"/value.txt'
    parser.testLexer(command)

  def test_parser(self):
    command = 'OpEn -param1->VAluE1 -ParaM2->"Value 2" -paRam_3->/"Value 3_1"/value.txt'
    print(parser.parser.parse(command))

if __name__ == "__main__":
  unittest.main()