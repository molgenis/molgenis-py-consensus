from unittest import TestCase

from parameterized import parameterized

from consensus.ConsensusFileGenerator import ConsensusFileGenerator


class ConsensusFileGeneratorTest(TestCase):
    file_generator = ConsensusFileGenerator(
        data={'consensus': {},
              'history': {
                  'history': {
                      '1912': ['1912_00299bb101', '1912_001759607f',
                               '1912_f2941cd0ea']},
                  'alternative': {
                      '1912': {
                          'ATP1A2_NM_000702.2:c.2841-20_2841-19insC': '1912_f2941cd0ea',
                          'PALB2_NM_024675.3:c.2928G>T': '1912_00299bb101'}
                  }}
              },
        tables={'consensus_table': '', 'comments_table': ''}, labs=[])

    def test__get_lab_classification(self):
        variant_classifications = {"LAB1": "b", "LAB2": "v", "LAB3": ""}
        variant = {"chromosome": "11", "start": "108167858", "ref": "T", "alt": "A", "gene": "ATM"}

        expected_string = '\tLAB1_4d11f6c3b0\tBenign'
        expected_bool = True

        observed_string, observed_bool = ConsensusFileGenerator._get_lab_classification(variant_classifications, 'LAB1',
                                                                                        variant)

        self.assertEqual(expected_string, observed_string)
        self.assertEqual(expected_bool, observed_bool)

    def test_create_consensus_header(self):
        labs = ['lab1', 'lab2', 'lab3']
        observed = ConsensusFileGenerator.create_consensus_header(labs)
        expected = 'id\tchromosome\tstart\tstop\tref\talt\tgene\tc_dna\ttranscript\tprotein\thgvs\t' \
                   'consensus_classification\tlab1_link\tlab1\tlab2_link\tlab2\tlab3_link\tlab3\tmatches\thistory\t' \
                   'disease\tcomments\n'
        self.assertEqual(expected, observed)

    def test__get_variant(self):
        observed = ConsensusFileGenerator._get_variant(1, 123, 'A', 'C', 'ABC1')
        expected = '1_123_A_C_ABC1'
        self.assertEqual(expected, observed)

    def test_create_consensus_line(self):
        variant_id = 'cfd99f1bea'
        variant = {'id': variant_id, 'chromosome': '1', 'start': 123, 'stop': 124, 'ref': 'A', 'alt': 'C',
                   'gene': 'ABC1', 'consensus_classification': '(Likely) benign', 'type': 'sub'}
        observed = self.file_generator._create_consensus_line('cfd99f1bea', variant,
                                                              {'lab1': 'lb', 'lab2': 'b', 'lab3': ''},
                                                              ['lab1', 'lab2', 'lab3'])
        expected = 'cfd99f1bea\t1\t123\t124\tA\tC\tABC1\t\t\t\t\t(Likely) benign\tLAB1_cfd99f1bea\tLikely benign\t' \
                   'LAB2_cfd99f1bea\tBenign\t\t\t2\t\t\tcfd99f1bea\n'
        self.assertEqual(expected, observed)

    @parameterized.expand([('empty', {}, 'test', '\t'),
                           ('column', {'column': 'value'}, 'column', '\tvalue')])
    def test__add_simple_column(self, _, variant, column, expected):
        line = ''
        observed = ConsensusFileGenerator._add_simple_column(line, variant, column)
        self.assertEqual(expected, observed)

    @parameterized.expand([('vus', 'VUS', 3, '\t3'),
                           ('no consensus', 'No consensus', 0, '\t'),
                           ('benign', '(Likely) benign', 5, '\t5'),
                           ('1lab', 'Classified by one lab', 1, '\t1')])
    def test__get_match_count_if_consensus(self, _, classification, matches, expected):
        observed = ConsensusFileGenerator._get_match_count_if_consensus(matches, classification)
        self.assertEqual(expected, observed)

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
         ['609ab27375', '3_38627166_C_CGTGTGTGTGTGTGG_SCN5A', '3_38627166_._GTGTGTGTGTGTGG_SCN5A']),
        ('delins',
         {'variant_id': '3e69715481', 'chromosome': '9', 'pos': '135786871', 'gene': 'TSC1', 'ref': 'GGGGAACTCAGAGT',
          'alt': 'AACTGC', 'variant_type': 'delins'},
         ['3e69715481', '9_135786871_GGGGAACTCAGAGT_AACTGC_TSC1', '4dd6e4fad5', '4b70f6a705', 'ae3fae1fd2',
          'c3d04968bc'])
    ])
    def test__get_history_ids_for_variant(self, _, variant_info, expected):
        variant_id = variant_info['variant_id']
        chromosome = variant_info['chromosome']
        pos = variant_info['pos']
        gene = variant_info['gene']
        ref = variant_info['ref']
        alt = variant_info['alt']
        variant_type = variant_info['variant_type']
        file_generator = ConsensusFileGenerator(
            data={'consensus': {},
                  'history': {
                      'history': {},
                      'alternative': {}}},
            tables={'consensus_table': '', 'comments_table': ''}, labs=[])
        observed = file_generator._get_history_ids_for_variant(variant_id, chromosome, pos, ref, alt, gene,
                                                               variant_type)
        self.assertEqual(observed, expected)

    def test__check_alternative_history(self):
        transcript = 'NM_000702.2'
        c_dna = 'c.2841-19delTinsCT'
        gene = 'ATP1A2'
        export = {'ATP1A2_NM_000702.2:c.2841-19delTinsCT': 'f2941cd0ea'}
        observed = ConsensusFileGenerator._check_alternative_history(transcript, c_dna, gene, export)
        self.assertEqual(observed, 'f2941cd0ea')

    @parameterized.expand([
        ('variant correct and has transcript:cDNA -> variant is correct',
         {'id': '00299bb101', 'ref': 'C', 'alt': 'A', 'start': 23634358, 'chromosome': '16', 'gene': 'PALB2',
          'type': 'sub', 'transcript': 'NM_024675.3', 'c_dna': 'c.2928G>T'}, ['1912_00299bb101']),
        ('variant correct and has no transcript:cDNA -> variant is correct',
         {'id': '001759607f', 'ref': 'G', 'alt': 'C', 'start': '108921331', 'chromosome': 'X', 'gene': 'ACSL4',
          'type': 'sub'}, ['1912_001759607f']),
        # f2941cd0ea
        ('variant incorrect and has transcript:cDNA -> merged with correct existing variant',
         {'id': '6a550d807b', 'ref': 'A', 'alt': 'AC', 'start': '160109408', 'chromosome': '1', 'gene': 'ATP1A2',
          'type': 'dup', 'transcript': 'NM_000702.2', 'c_dna': 'c.2841-20_2841-19insC'}, ['1912_f2941cd0ea']),
        ('variant incorrect and has no transcript:cDNA -> new variant',
         {'id': '6a550d807b', 'ref': 'A', 'alt': 'AC', 'start': '160109408', 'chromosome': '1', 'gene': 'ATP1A2',
          'type': 'dup'}, [])
    ])
    def test___get_matching_history(self, _, variant, expected):
        observed = self.file_generator._get_matching_history(variant)
        self.assertEqual(observed, expected)
