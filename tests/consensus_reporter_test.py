import unittest, os

from consensus.ConsensusReporter import ConsensusReporter


class TestStringMethods(unittest.TestCase):
    cr = ConsensusReporter

    def _initialize_cr(self):
        # Initialise consensus table generator with test data
        molgenis_server = None
        labs = ['lab1', 'lab2', 'lab3']
        prefix = 'test_'
        csv = prefix + 'test.csv'
        csv_file = open(csv, 'w')
        test_content = '"id","chromosome","start","stop","ref","alt","gene","c_dna","transcript","protein",\
                       "consensus_classification","lab1_link","lab1","lab2_link","lab2","matches","history",\
                       "disease","comments\n1_12345678_A_C_ABC1","1","12345678","12345678","A","C","ABC1",\
                       "c.1234A>C","NM_000012.3","p.A594V","VUS","LAB1_1_12345678_A_C_ABC1","VUS",\
                       "LAB2_1_12345678_A_C_ABC1","VUS","2","1801_1_12345678_A_C_ABC1,1803_1_12345678_A_C_ABC1","",\
                       "1_12345678_A_C_ABC1"'
        csv_file.write(test_content)
        csv_file.close()
        public = prefix + 'public'
        cr = self.cr(csv, molgenis_server, labs, public, prefix)

        return cr

    @classmethod
    def tearDownClass(cls):
        os.remove('test_counts.html')
        os.remove('test_test.csv')
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
        cr = self._initialize_cr()

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