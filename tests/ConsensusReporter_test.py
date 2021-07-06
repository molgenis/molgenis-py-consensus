import io
import os
import shutil
from datetime import datetime
from unittest import TestCase

from consensus.ConsensusReporter import ConsensusReporter


class TestConsensusReporter(TestCase):
    @classmethod
    def setUpClass(cls):
        prefix = 'test_'
        cls.tmp_dir = '..{}test_data{}tmp{}'.format(os.sep, os.sep, os.sep)
        if not os.path.exists(cls.tmp_dir):
            os.mkdir(cls.tmp_dir)
        shutil.copyfile('..{}test_data{}test_consensus.csv'.format(os.sep, os.sep),
                        '{}test_consensus.csv'.format(cls.tmp_dir))
        output = cls.tmp_dir
        labs = ['lab1', 'lab2', 'lab3', 'lab4', 'lab5', 'lab6', 'lab7', 'lab8']
        csv = '{}{}consensus.csv'.format(output, prefix)
        public = prefix + 'public_consensus'
        cls.reporter = ConsensusReporter(csv, labs, public, prefix, output)

    def test_count_classifications(cls):
        counts = cls.reporter.count_classifications()
        cls.assertEqual(counts['(Likely) benign'], 20)
        cls.assertEqual(counts['(Likely) pathogenic'], 1)
        cls.assertEqual(counts['Classified by one lab'], 9)
        cls.assertEqual(counts['No consensus'], 1)
        cls.assertEqual(counts['Opposite classifications'], 1)

    def test_count_single_classifications(cls):
        singles = cls.reporter.count_single_classifications()
        cls.assertEqual(singles['Benign'], 2)
        cls.assertEqual(singles['Likely benign'], 4)
        cls.assertEqual(singles['Pathogenic'], 1)
        cls.assertEqual(singles['VUS'], 2)

    def test_create_public_table(cls):
        public = cls.reporter.create_public_table()
        cls.assertEqual(len(public), 30)

    def test_write_opposites(cls):
        cls.reporter.write_opposites()
        month_year = datetime.now().strftime("%y%m")
        snapshot = io.open('..{}test_data{}test_opposites_report_snapshot.tsv'.format(os.sep, os.sep))
        actual = io.open('{}test_opposites_report_{}.tsv'.format(cls.tmp_dir, month_year))
        cls.assertListEqual(
            list(actual),
            list(snapshot))
        snapshot.close()
        actual.close()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp_dir)
