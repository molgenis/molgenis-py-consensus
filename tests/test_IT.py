import glob
import os
import unittest
from datetime import datetime

from consensus import __main__
from preprocessing import PreProcessor


class TestIT(unittest.TestCase):
    def test_assert_output_files(self):
        PreProcessor.main('test_data/config/config_test.txt')
        __main__.main('test_data/config/config_test.txt')
        expected_output_content = ['.gitignore', 'incorrect_variant_history.tsv', 'vkgl_amc.tsv',
                                   'vkgl_comments.tsv', 'vkgl_consensus.tsv',
                                   'vkgl_consensus_comments.tsv', 'vkgl_counts.html',
                                   'vkgl_delins.tsv',
                                   'vkgl_erasmus.tsv', 'vkgl_log.tsv', 'vkgl_lumc.tsv',
                                   'vkgl_nki.tsv',
                                   'vkgl_opposites_report_' + datetime.now().strftime(
                                       "%y%m") + '.tsv', 'vkgl_public_consensus.tsv',
                                   'vkgl_radboud_mumc.tsv', 'vkgl_types.txt', 'vkgl_umcg.tsv',
                                   'vkgl_umcu.tsv', 'vkgl_vumc.tsv']
        self.assertCountEqual(os.listdir('test_data/output'), expected_output_content)

    def tearDown(self):
        files = glob.glob('test_data/output/*')
        for f in files:
            if not f == '.gitignore':
                os.remove(f)
