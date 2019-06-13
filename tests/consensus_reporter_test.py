import unittest, os

from consensus.ConsensusReporter import ConsensusReporter


class TestStringMethods(unittest.TestCase):
    cr = ConsensusReporter

    def _initialize_ctg(self):
        # Initialise consensus table generator with test data
        csv = 'test.csv'
        csv_file = open(csv, 'w')
        csv_file.close()
        molgenis_server = None
        labs = ['lab1', 'lab2', 'lab3']
        public = 'public'
        cr = self.cr(csv, molgenis_server, labs, public, True)

        return cr

    @classmethod
    def tearDownClass(cls):
        os.remove('public.csv')
        os.remove('test.txt')
        os.remove('test.html')
        os.remove('test.csv')
        os.remove('test_log.txt')
        os.remove('test_types.txt')

    def test_convert_classification(self):
        expected_b = 'LB'
        expected_p = 'LP'
        expected_v = 'VUS'

        classification1 = 'Likely benign'
        observed1 = self.cr.convert_classification(classification1)
        self.assertEqual(expected_b, observed1)

        classification2 = '(Likely) benign'
        observed2 = self.cr.convert_classification(classification2)
        self.assertEqual(expected_b, observed2)

        classification3 = 'Pathogenic'
        observed3 = self.cr.convert_classification(classification3)
        self.assertEqual(expected_p, observed3)

        classification4 = 'VUS'
        observed4 = self.cr.convert_classification(classification4)
        self.assertEqual(expected_v, observed4)

    def test_get_single_lab_classification(self):
        cr = self._initialize_ctg()

        column_map = {'lab1': 0, 'lab2': 1, 'lab3': 2, 'classification': 3}

        variant1 = ['Likely benign', '', '', 'Classified by one lab']
        observed1 = cr.get_single_lab_classification(variant1, column_map)
        expected1 = 'Likely benign'
        self.assertEqual(expected1, observed1)

        variant2 = ['', 'Pathogenic', '', 'Classified by one lab']
        observed2 = cr.get_single_lab_classification(variant2, column_map)
        expected2 = 'Pathogenic'
        self.assertEqual(expected2, observed2)

        variant3 = ['', '', 'VUS', 'Classified by one lab']
        observed3 = cr.get_single_lab_classification(variant3, column_map)
        expected3 = 'VUS'
        self.assertEqual(expected3, observed3)

    def test_get_column_positions(self):
        header = ['col1', 'col2', 'col3']
        observed = self.cr._get_column_positions(header)
        expected = {'col1': 0, 'col2': 1, 'col3': 2}
        self.assertEqual(expected, observed)

    def test_count_types(self):
        cr = self._initialize_ctg()

        column_map = {'lab1': 0, 'lab2': 1, 'lab3': 2, 'ref': 3, 'alt': 4}

        variant1 = ['Benign', '', '', 'A', 'G']  # snp, lab1
        variant2 = ['Pathogenic', 'Likely pathogenic', 'Likely pathogenic', '.', 'G']  # ins, lab1, lab2, lab3
        variant3 = ['Pathogenic', '', 'Likely pathogenic', 'G', '.']  # del, lab1, lab3
        variant4 = ['Benign', 'Likely pathogenic', 'Likely pathogenic', 'A', 'AG']  # ins, lab1, lab2, lab3
        variant5 = ['Pathogenic', 'VUS', 'Likely benign', 'GA', 'G']  # del, lab1, lab2, lab3
        variant6 = ['', 'VUS', 'VUS', 'GAGA', 'AGCG']  # delins, lab2, lab3
        variant7 = ['', 'Benign', 'VUS', 'GAGA', 'GAGG']  # snp, lab2, lab3

        variants = [variant1, variant2, variant3, variant4, variant5, variant6, variant7]

        for variant in variants:
            cr.count_type(variant, column_map)

        self.assertEqual(1, cr.types['lab1']['snp'])  # variant1
        self.assertEqual(1, cr.types['lab2']['snp'])  # variant7
        self.assertEqual(1, cr.types['lab3']['snp'])  # variant2

        self.assertEqual(2, cr.types['lab1']['ins'])  # variant2,variant4
        self.assertEqual(2, cr.types['lab2']['ins'])  # variant2,variant4
        self.assertEqual(2, cr.types['lab3']['ins'])  # variant2,variant4

        self.assertEqual(2, cr.types['lab1']['del'])  # variant3,variant5
        self.assertEqual(1, cr.types['lab2']['del'])  # variant3
        self.assertEqual(2, cr.types['lab3']['del'])  # variant3,variant5

        self.assertEqual(0, cr.types['lab1']['delins'])  # no variants
        self.assertEqual(1, cr.types['lab2']['delins'])  # variant6
        self.assertEqual(1, cr.types['lab3']['delins'])  # variant6
