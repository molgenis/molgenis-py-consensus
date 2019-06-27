import unittest
from parameterized import parameterized

from consensus.ConsensusTableGenerator import ConsensusTableGenerator


class TestConsensusTableGenerator(unittest.TestCase):
    ctg = ConsensusTableGenerator
    # Lab test data
    lab_labels = {'lab_b': 'LABB', 'lab_p': 'LABP', 'lab_vus': 'LABVUS'}
    labs = {
        'lab1': {'alt': 'G',
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
                 'transcript': 'NM_000051.3'},
        'lab_b': {'alt': 'G',
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
                  'transcript': 'NM_000051.3'},
        'lab_p': {'alt': 'G',
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
                  'transcript': 'NM_000051.3'},
        'lab_vus': {'alt': 'G',
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

    }
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

    @parameterized.expand([
        ('consensus_benign', 'lab_b', '(Likely) benign', 2),
        ('no_consensus', 'lab_vus', 'No consensus', 1),
        ('opposite', 'lab_p', 'Opposite classifications', 1)
    ])
    def test_update_variant_classification_2(self, _, lab_id, expected_label,
                                             expected_total):
        lab2_label = self.lab_labels[lab_id]
        lab2 = self.labs[lab_id]
        # Lab test data in one dict
        lab_data = {'LAB1': [self.labs['lab1']], lab2_label: [lab2]}

        ctg = self._initialize_ctg(lab_data, 'Classified by one lab')

        # Call function to test
        ctg.update_variant_classification(self.consensus_id, lab2, lab2_label)

        # Classification to observe
        observed_class = ctg.all_variants[self.consensus_id]['consensus_classification']

        expected_class = lab2['classification']['id']

        # Test observed outcome
        self.assertEqual(expected_label, observed_class)
        self.assertEqual(expected_class, ctg.all_lab_classifications[self.consensus_id][lab2_label])
        self.assertEqual(expected_total, ctg.all_classifications[self.consensus_id][expected_class])

    @parameterized.expand([
        ('no_consensus', 'lab_vus', 'lab_b', 'No consensus', 'No consensus', 2),
        ('opposite', 'lab_p', 'lab_vus', 'Opposite classifications', 'Opposite classifications', 1),
        ('new_opposite', 'lab_vus', 'lab_p', 'No consensus', 'Opposite classifications', 1)
    ])
    def test_update_variant_classification_3(self, _, lab2_id, lab3_id, classification, expected_label, expected_total):
        lab2 = self.labs[lab2_id]
        lab2_label = self.lab_labels[lab2_id]

        lab3 = self.labs[lab3_id]
        lab3_label = self.lab_labels[lab3_id]

        # Lab test data in one dict
        lab_data = {'LAB1': [self.labs['lab1']], lab2_label: [lab2], lab3_label: [lab3]}

        ctg = self._initialize_ctg(lab_data, classification)

        # Call function to test
        ctg.update_variant_classification(self.consensus_id, lab3, lab3_label)

        # Classification to observe
        observed_class = ctg.all_variants[self.consensus_id]['consensus_classification']

        expected_class = lab3['classification']['id']

        # Test observed outcome
        self.assertEqual(expected_label, observed_class)
        self.assertEqual(expected_class, ctg.all_lab_classifications[self.consensus_id][lab3_label])
        self.assertEqual(expected_total, ctg.all_classifications[self.consensus_id][expected_class])
