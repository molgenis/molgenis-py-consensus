import unittest

import mock

from consensus.TsvToListConverter import TsvToListConverter


class TestTsvToListConverter(unittest.TestCase):
    def test_parse(self):
        with mock.patch('consensus.TsvToListConverter.open',
                        mock.mock_open(read_data='"col1"\t"col2"\t"col3"\n"val1"\t"val2"\t"val3"\n'),
                        create=True) as m:
            result = TsvToListConverter.parse("filename")
            self.assertEqual(result, [{'col1': 'val1', 'col2': 'val2', 'col3': 'val3'}])


if __name__ == '__main__':
    unittest.main()
