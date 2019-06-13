import unittest

from consensus.ConsensusTableGenerator import ConsensusTableGenerator


class TestStringMethods(unittest.TestCase):
    ctg = ConsensusTableGenerator
    # Lab test data
    lab1 = {'alt': 'G',
            'c_dna': 'c.146C>G',
            'chromosome': '11',
            'classification': {'id': 'b',
                               'label': 'Benign'},
            'gene': 'ATM',
            'id': 'BLAB_11_108098576_C_G_ATM',
            'protein': 'p.S49C',
            'ref': 'C',
            'start': 108098576,
            'stop': 108098576,
            'transcript': 'NM_000051.3'}

    lab_b = {'alt': 'G',
             'c_dna': 'c.146C>G',
             'chromosome': '11',
             'classification': {'id': 'b',
                                'label': 'Benign'},
             'gene': 'ATM',
             'id': 'LABB_11_108098576_C_G_ATM',
             'protein': 'p.S49C',
             'ref': 'C',
             'start': 108098576,
             'stop': 108098576,
             'transcript': 'NM_000051.3'}

    lab_p = {'alt': 'G',
             'c_dna': 'c.146C>G',
             'chromosome': '11',
             'classification': {'id': 'p',
                                'label': 'Pathogenic'},
             'gene': 'ATM',
             'id': 'LABP_11_108098576_C_G_ATM',
             'protein': 'p.S49C',
             'ref': 'C',
             'start': 108098576,
             'stop': 108098576,
             'transcript': 'NM_000051.3'}

    lab_vus = {'alt': 'G',
               'c_dna': 'c.146C>G',
               'chromosome': '11',
               'classification': {'id': 'vus',
                                  'label': 'VUS'},
               'gene': 'ATM',
               'id': 'LABVUS_11_108098576_C_G_ATM',
               'protein': 'p.S49C',
               'ref': 'C',
               'start': 108098576,
               'stop': 108098576,
               'transcript': 'NM_000051.3'}

    consensus_id = 'consensus_11_108098576_C_G_ATM'

    def _initialize_ctg(self, lab_data, current_class):
        # Initialise consensus table generator with test data
        ctg = self.ctg(lab_data)
        lab_ids = list(dict.keys(lab_data))

        # Last variant should not be added yet
        initial_labs = lab_ids[0:len(lab_ids) - 1]

        # Dict with as key the id of the variant in the consensus and as value another dict
        # with as key the id of the lab and as value the id of its classification (b/lb/vus/lp/p)
        lab_classifications = {lab_id: lab_data[lab_id][0]['classification']['id'] for lab_id in initial_labs}

        ctg.all_lab_classifications = {self.consensus_id: lab_classifications}

        ctg.all_classifications = {self.consensus_id: {'b': 0, 'lb': 0, 'lp': 0, 'p': 0, 'vus': 0}}

        for lab_id in initial_labs:
            classification = lab_data[lab_id][0]['classification']['id']
            ctg.all_classifications[self.consensus_id][classification] += 1

        ctg.all_variants = {
            self.consensus_id: {'alt': 'G',
                           'c_dna': 'c.146C>G',
                           'chromosome': '11',
                           'consensus_classification': current_class,
                           'gene': 'ATM',
                           'protein': 'p.S49C',
                           'ref': 'C',
                           'start': 108098576,
                           'stop': 108098576,
                           'transcript': 'NM_000051.3'}}
        return ctg

    def test_is_no_consensus(self):
        no_consensus = {'vus': 1, 'b': 1, 'lb': 1, 'p': 0, 'lp': 0}
        self.assertTrue(self.ctg._is_no_consensus(no_consensus))
        vus = {'vus': 2, 'b': 0, 'lb': 0, 'p': 0, 'lp': 0}
        self.assertFalse(self.ctg._is_no_consensus(vus))
        p = {'vus': 0, 'b': 0, 'lb': 0, 'p': 1, 'lp': 1}
        self.assertFalse(self.ctg._is_no_consensus(p))
        b = {'vus': 0, 'b': 1, 'lb': 1, 'p': 0, 'lp': 0}
        self.assertFalse(self.ctg._is_no_consensus(b))
        opposite = {'vus': 1, 'b': 1, 'lb': 1, 'p': 1, 'lp': 0}
        # Opposite is a form of "no consensus"
        self.assertTrue(self.ctg._is_no_consensus(opposite))

    def test_is_conflicting_classification(self):
        no_consensus = {'vus': 1, 'b': 1, 'lb': 1, 'p': 0, 'lp': 0}
        self.assertFalse(self.ctg._is_conflicting_classification(no_consensus))
        vus = {'vus': 2, 'b': 0, 'lb': 0, 'p': 0, 'lp': 0}
        self.assertFalse(self.ctg._is_conflicting_classification(vus))
        p = {'vus': 0, 'b': 0, 'lb': 0, 'p': 1, 'lp': 1}
        self.assertFalse(self.ctg._is_conflicting_classification(p))
        b = {'vus': 0, 'b': 1, 'lb': 1, 'p': 0, 'lp': 0}
        self.assertFalse(self.ctg._is_conflicting_classification(b))
        opposite = {'vus': 1, 'b': 1, 'lb': 1, 'p': 1, 'lp': 0}
        self.assertTrue(self.ctg._is_conflicting_classification(opposite))

    def test_get_classification(self):
        vus = 'vus'
        self.assertEqual('VUS', self.ctg._get_classification(vus))
        lp = 'lp'
        self.assertEqual('(Likely) pathogenic', self.ctg._get_classification(lp))
        p = 'p'
        self.assertEqual('(Likely) pathogenic', self.ctg._get_classification(p))
        lb = 'lb'
        self.assertEqual('(Likely) benign', self.ctg._get_classification(lb))
        b = 'b'
        self.assertEqual('(Likely) benign', self.ctg._get_classification(b))

    def test_update_variant_classification_consensus(self):
        lab2 = self.lab_b
        lab2_label = 'LABB'

        # Lab test data in one dict
        lab_data = {'LAB1': [self.lab1], lab2_label: [lab2]}

        ctg = self._initialize_ctg(lab_data, 'Classified by one lab')

        # Call function to test
        ctg.update_variant_classification(self.consensus_id, lab2, lab2_label)

        # Classification to observe
        observed_class = ctg.all_variants[self.consensus_id]['consensus_classification']

        # Expected outcome
        expected_class = 'b'
        expected_label = '(Likely) benign'
        expected_total = 2

        # Test observed outcome
        self.assertEqual(expected_label, observed_class)
        self.assertEqual(expected_class, ctg.all_lab_classifications[self.consensus_id][lab2_label])
        self.assertEqual(expected_total, ctg.all_classifications[self.consensus_id][expected_class])

    def test_update_variant_classification_no_consensus(self):
        lab2 = self.lab_vus
        lab2_label = 'LABVUS'

        # Lab test data in one dict
        lab_data = {'LAB1': [self.lab1], lab2_label: [lab2]}

        ctg = self._initialize_ctg(lab_data, 'Classified by one lab')

        # Call function to test
        ctg.update_variant_classification(self.consensus_id, lab2, lab2_label)

        # Classification to observe
        observed_class = ctg.all_variants[self.consensus_id]['consensus_classification']

        # Expected outcome
        expected_class = 'vus'
        expected_label = 'No consensus'
        expected_total = 1

        # Test observed outcome
        self.assertEqual(expected_label, observed_class)
        self.assertEqual(expected_class, ctg.all_lab_classifications[self.consensus_id][lab2_label])
        self.assertEqual(expected_total, ctg.all_classifications[self.consensus_id][expected_class])

    def test_update_variant_classification_opposite(self):
        lab2 = self.lab_p
        lab2_label = 'LABP'

        # Lab test data in one dict
        lab_data = {'LAB1': [self.lab1], lab2_label: [lab2]}

        ctg = self._initialize_ctg(lab_data, 'Classified by one lab')

        # Call function to test
        ctg.update_variant_classification(self.consensus_id, lab2, lab2_label)

        # Classification to observe
        observed_class = ctg.all_variants[self.consensus_id]['consensus_classification']

        # Expected outcome
        expected_class = 'p'
        expected_label = 'Opposite classifications'
        expected_total = 1

        # Test observed outcome
        self.assertEqual(expected_label, observed_class)
        self.assertEqual(expected_class, ctg.all_lab_classifications[self.consensus_id][lab2_label])
        self.assertEqual(expected_total, ctg.all_classifications[self.consensus_id][expected_class])

    def test_update_variant_classification_no_consensus_3rd_lab(self):
        lab2 = self.lab_vus
        lab2_label = 'LABVUS'

        lab3 = self.lab_b
        lab3_label = 'LABB'

        # Lab test data in one dict
        lab_data = {'LAB1': [self.lab1], lab2_label: [lab2], lab3_label: [lab3]}

        ctg = self._initialize_ctg(lab_data, 'No consensus')

        # Call function to test
        ctg.update_variant_classification(self.consensus_id, lab3, lab3_label)

        # Classification to observe
        observed_class = ctg.all_variants[self.consensus_id]['consensus_classification']

        # Expected outcome
        expected_class = 'b'
        expected_label = 'No consensus'
        expected_total = 2

        # Test observed outcome
        self.assertEqual(expected_label, observed_class)
        self.assertEqual(expected_class, ctg.all_lab_classifications[self.consensus_id][lab3_label])
        self.assertEqual(expected_total, ctg.all_classifications[self.consensus_id][expected_class])

    def test_update_variant_classification_opposite_3rd_lab(self):
        lab2 = self.lab_p
        lab2_label = 'LABP'

        lab3 = self.lab_vus
        lab3_label = 'LABVUS'

        # Lab test data in one dict
        lab_data = {'LAB1': [self.lab1], lab2_label: [lab2], lab3_label: [lab3]}

        ctg = self._initialize_ctg(lab_data, 'Opposite classifications')

        # Call function to test
        ctg.update_variant_classification(self.consensus_id, lab3, lab3_label)

        # Classification to observe
        observed_class = ctg.all_variants[self.consensus_id]['consensus_classification']

        # Expected outcome
        expected_class = 'vus'
        expected_label = 'Opposite classifications'
        expected_total = 1

        # Test observed outcome
        self.assertEqual(expected_label, observed_class)
        self.assertEqual(expected_class, ctg.all_lab_classifications[self.consensus_id][lab3_label])
        self.assertEqual(expected_total, ctg.all_classifications[self.consensus_id][expected_class])

    def test_update_variant_classification_new_opposite_3rd_lab(self):
        lab2 = self.lab_vus
        lab2_label = 'LABVUS'

        lab3 = self.lab_p
        lab3_label = 'LABP'

        # Lab test data in one dict
        lab_data = {'LAB1': [self.lab1], lab2_label: [lab2], lab3_label: [lab3]}

        ctg = self._initialize_ctg(lab_data, 'No consensus')

        # Call function to test
        ctg.update_variant_classification(self.consensus_id, lab3, lab3_label)

        # Classification to observe
        observed_class = ctg.all_variants[self.consensus_id]['consensus_classification']

        # Expected output
        expected_class = 'p'
        expected_label = 'Opposite classifications'
        expected_total = 1

        # Test observed output
        self.assertEqual(expected_label, observed_class)
        self.assertEqual(expected_class, ctg.all_lab_classifications[self.consensus_id][lab3_label])
        self.assertEqual(expected_total, ctg.all_classifications[self.consensus_id][expected_class])
