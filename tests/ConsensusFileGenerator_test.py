from unittest import TestCase
from parameterized import parameterized
from consensus.ConsensusFileGenerator import ConsensusFileGenerator


class ConsensusFileGeneratorTest(TestCase):

    def test__get_lab_classification(self):
        variant_classifications = {"LAB1": "b", "LAB2": "v", "LAB3": ""}
        variant = {"chromosome": "11", "start": "108167858", "ref": "T", "alt": "A", "gene": "ATM"}

        expected_string = ',"LAB1_4d11f6c3b0","Benign"'
        expected_bool = True

        observed_string, observed_bool = ConsensusFileGenerator._get_lab_classification(variant_classifications, 'LAB1',
                                                                                        variant)

        self.assertEqual(expected_string, observed_string)
        self.assertEqual(expected_bool, observed_bool)

    @parameterized.expand([
        ('sub',
         {'variant_id': '5d0cf0e376', 'chromosome': '10', 'pos': '112540884', 'gene': 'RBM20', 'ref': 'C', 'alt': 'A',
          'variant_type': 'sub'}, ['5d0cf0e376', '10_112540884_C_A_RBM20']),
        ('del',
         {'variant_id': '5ef356611e', 'chromosome': '8', 'pos': '41573267', 'gene': 'ANK1', 'ref': 'GCGGTGGTGGC',
          'alt': 'G', 'variant_type': 'del'},
         ['5ef356611e', '8_41573267_GCGGTGGTGGC_G_ANK1', '8_41573268_CGGTGGTGGC_._ANK1']),
        ('ins',
         {'variant_id': '609ab27375', 'chromosome': '3', 'pos': '38627166', 'gene': 'SCN5A', 'ref': 'C',
          'alt': 'CGTGTGTGTGTGTGG', 'variant_type': 'ins'},
         ['609ab27375', '3_38627166_C_CGTGTGTGTGTGTGG_SCN5A', '3_38627166_._GTGTGTGTGTGTGG_SCN5A'])
    ])
    def test__get_history_ids_for_variant(self, _, variant_info, expected):
        variant_id = variant_info['variant_id']
        chromosome = variant_info['chromosome']
        pos = variant_info['pos']
        gene = variant_info['gene']
        ref = variant_info['ref']
        alt = variant_info['alt']
        variant_type = variant_info['variant_type']
        observed = ConsensusFileGenerator._get_history_ids_for_variant(variant_id, chromosome, pos, ref, alt, gene,
                                                                       variant_type)
        self.assertEqual(observed, expected)
