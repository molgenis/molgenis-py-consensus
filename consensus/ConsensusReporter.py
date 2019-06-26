import datetime
import re
import sys
import time
import pandas
import progressbar
import csv
from molgenis import client as molgenis
from consensus.MolgenisConfigParser import MolgenisConfigParser as ConfigParser
from consensus.Variants import Variants
from yaspin import yaspin
from termcolor import cprint, colored


class ConsensusReporter:
    """ConsensusReporter generates a log file with all opposites and on the bottom the counts in HTML format and a
    public consensus table."""

    def __init__(self, consensus_csv, session, labs, public_consensus, prefix):
        self.labs = labs
        report_id = self._get_month_and_year()

        self.opposites_file_name = prefix + 'opposites_report_{}.txt'.format(report_id)
        self.counts_file_name = prefix + 'counts.html'
        self.type_file_name = prefix + 'types.txt'
        self.log_file_name = prefix + 'log.csv'
        self.delins_file_name = prefix + 'delins.csv'
        self.public_consensus_file_name = public_consensus + '.csv'

        # Open output files
        self.report = open(self.opposites_file_name, 'w')
        self.type_file = open(self.type_file_name, 'w')
        self.counts_html = open(self.counts_file_name, 'w')
        self.public_consensus_table = public_consensus
        self.molgenis_server = session

        # Prevent stop position from getting converted to float because it's optional
        self.consensus_df = pandas.read_csv(consensus_csv, low_memory=False, converters={'stop': str},
                                            na_values={'stop': ''})

    def _synchronous_upload(self, file_name):
        """
        Uploads data from csv file to molgenis table
        :param file_name: name of the file to upload (should be *fully qualified name here*.csv)
        :return: True if Finishes
        :raises ImportError if import failed
        """
        response = self.molgenis_server.upload_zip(file_name).split('/')
        run_entity_type = response[-2]
        run_id = response[-1]
        status_info = self.molgenis_server.get_by_id(run_entity_type, run_id)

        with yaspin(text='Updating public consensus', color='green') as spinner:
            while status_info['status'] == 'RUNNING':
                time.sleep(2)
                status_info = self.molgenis_server.get_by_id(run_entity_type, run_id)

            if status_info['status'] == 'FINISHED':
                spinner.ok('✔')
            else:
                spinner.fail('💥')
                cprint("Error while uploading [{}]: {}".format(file_name, status_info['message']), 'red',
                       attrs=['bold'],
                       file=sys.stderr)

    def delete_public_consensus(self, table):
        """
        Deletes the content of the public consensus table
        :param table: the name of the public consensus table
        :return: None
        """
        with yaspin(text='Deleting current public consensus', color='green') as spinner:
            try:
                self.molgenis_server.delete(table)
                spinner.ok('✔')
            except Exception as e:
                spinner.fail('💥')
                cprint("Error while deleting data from [{}]: {}".format(table, e), 'red', attrs=['bold'],
                       file=sys.stderr)

    def count_classifications(self):
        """
        Groups the consensus dataframe by consensus classification to return its counts
        :return: Series with number of variants per classification
        """
        grouped = self.consensus_df.groupby('consensus_classification')
        return grouped.id.count()

    def count_single_classifications(self):
        """
        Filters the consensus dataframe on "Classified by one lab" classification, melts that table to get one line
        per lab and returns the count (count doesnt count NA's)
        :return: Number of single lab classifications
        """
        one_lab = self.consensus_df[self.consensus_df.consensus_classification == 'Classified by one lab']
        return pandas.melt(one_lab, id_vars=['id'], value_vars=self.labs, var_name="lab", value_name="classification") \
            .groupby('classification') \
            .classification \
            .count()

    def create_public_table(self):
        """
        Creates a dataframe with all variants that have a single lab classification and the variants with consensus.
        :return: dataframe with all variants that should be in the public consensus table
        """
        one_lab_label = 'Classified by one lab'
        is_consensus = (self.consensus_df.consensus_classification != 'Opposite classifications') & \
                       (self.consensus_df.consensus_classification != 'No consensus') & \
                       (self.consensus_df.consensus_classification != one_lab_label)

        # Get consensus rows with "Classified by one lab" classification
        one_lab = self.consensus_df[self.consensus_df.consensus_classification == one_lab_label].copy()
        # The first (and only) lab that has a non missing value for the classification is the classification
        one_lab_classification = one_lab.loc[:, self.labs].bfill(1).iloc[:, 0]
        # Overwrite "Classified by one lab" with the lab's converted classification
        one_lab['consensus_classification'] = one_lab_classification
        one_lab['support'] = '1 lab'
        consensus = self.consensus_df[is_consensus].copy()
        consensus['support'] = consensus['matches'].apply(lambda x: str(round(x)) + ' labs')

        # Merge consensus classification with one lab
        public = consensus.append(one_lab)
        public['label'] = public.apply(
            lambda x: '{}:{} {} {}>{}'.format(x.chromosome, str(x.start), x.gene, x.ref, x.alt), axis=1)
        public['c_notation'] = public['c_dna']
        public['p_notation'] = public['protein']
        public['classification'] = public['consensus_classification'].apply(self.convert_classification)
        return public

    def write_public_table(self):
        """
        Generates a csv file for the public consensus table.
        :return: None
        """
        public = self.create_public_table()
        public.to_csv(self.public_consensus_file_name, index=False,
                      columns=['id', 'label', 'chromosome', 'start', 'stop', 'ref', 'alt', 'c_notation', 'p_notation',
                               'transcript', 'gene', 'support', 'classification'], quoting=csv.QUOTE_NONNUMERIC)

    def process_consensus(self):
        """
        Processes the lines in the consensus csv to generate reports (public consensus, counts, delins, log and a list
        of opposites)
        :return: None
        """
        progress = progressbar.ProgressBar(max_value=8)

        print('Generating reports')
        self.count_classifications()
        progress.update(1)
        self.write_opposites()
        progress.update(2)
        self.write_public_table()
        progress.update(4)
        self.write_variant_types()
        progress.update(6)
        self.write_count_output()
        progress.update(7)
        self.quality_check()
        progress.update(8)
        progress.finish()

        print('Generated [{}], [{}], [{}], [{}], [{}], and [{}]\n'.format(colored(self.opposites_file_name, 'blue'),
                                                              colored(self.counts_file_name, 'blue'),
                                                              colored(self.type_file_name, 'blue'),
                                                              colored(self.public_consensus_file_name, 'blue'),
                                                              colored(self.delins_file_name, 'blue'),
                                                              colored(self.log_file_name, 'blue')))
        # Close in and output files
        self.report.close()
        self.counts_html.close()
        self.type_file.close()

        # Upload public consensus
        self.delete_public_consensus(self.public_consensus_table)
        self._synchronous_upload(self.public_consensus_file_name)

    @staticmethod
    def convert_classification(classification):
        """
        Converts classifications into their ids
        :param classification: the classification to convert
        :return: the converted classification
        """
        classifications = {'benign': 'LB', 'vus': 'VUS', 'pathogenic': 'LP'}
        stripped_class = re.sub(r'\(?likely\)? ', '', classification.lower())
        return classifications[stripped_class]

    def get_single_lab_classification(self, variant, column_map):
        """
        Returns the classification of the lab for variants with only one classification
        :param variant: the variant that was classified by one lab
        :param column_map: the dictionary with the position of each column in the consensus csv
        :return: the classification of the variant (classified by one lab)
        """
        return [variant[column_map[lab]] for lab in self.labs if variant[column_map[lab]] != ''][0]

    @staticmethod
    def _get_month_and_year():
        """
        Retrieves the current year and month
        :return: the last two numbers of the year followed by the two numbers of the month
        """
        return datetime.datetime.now().strftime("%y%m")

    def write_opposites(self):
        opposites = self.consensus_df[self.consensus_df.consensus_classification == 'Opposite classifications']
        for row in opposites.iterrows():
            self.write_opposites_line(row[1])

    def write_opposites_line(self, variant):
        """
        Writes a variant with an opposite classification to the opposites log file.
        :param variant: The variant to add to the file (Series with chromosome, stop, ref, alt, gene, labs)
        :return: None
        """
        classifications = {lab: variant[lab] for lab in self.labs if type(variant[lab]) == str}

        self.report.write('{}:{}-{}\tREF:{}\tALT:{}\t({})\n'.format(variant.chromosome,
                                                                    variant.start,
                                                                    variant.stop,
                                                                    variant.ref,
                                                                    variant.alt,
                                                                    variant.gene))
        for lab in classifications:
            self.report.write('{}: {}\n'.format(lab, classifications[lab]))
        self.report.write('\n')

    def write_count_output(self):
        """
        Writes a HTML file with the consensus counts (how many times classifications were used)
        :return: None
        """
        moment = datetime.datetime.now().strftime("%B %Y")
        counts = self.count_classifications()
        single_counts = self.count_single_classifications()
        one_lab = 'Classified by one lab'

        self.counts_html.write('<h1>Counts for {} export</h1>\n<ul>\n'.format(moment))

        for classification, count in counts.iteritems():
            if classification != one_lab:
                self.counts_html.write('\t<li>{}: {}</li>\n'.format(classification, count))

        self.counts_html.write('\t<li>Classified by one lab ({}):\n\t\t<ul>\n'.format(str(counts[one_lab])))

        for classification, count in single_counts.iteritems():
            self.counts_html.write('\t\t\t<li>{}: {}</li>\n'.format(classification, count))

        self.counts_html.write('\t\t</ul>\n\t</li>\n</ul>')

    def quality_check(self):
        """
        Check for each ref/alt if it needs simplification (Variants.need_simplification) and writes variants that need
        simplification to a log file.
        :return: None
        """
        self.consensus_df['simplification'] = self.consensus_df.apply(
            lambda x: Variants.need_simplification(x.ref, x.alt), axis=1)
        columns = ['id', 'chromosome', 'start', 'stop', 'ref', 'alt', 'c_dna', 'protein', 'transcript', 'gene',
                   'consensus_classification'] + self.labs
        self.consensus_df.loc[lambda x: x.simplification].to_csv(self.log_file_name, index=False, columns=columns,
                                                                 quoting=csv.QUOTE_NONNUMERIC)

    def write_delins_file(self, consensus_with_type):
        """
        Writes delins variants to a seperate file
        :param consensus_with_type: the consensus dataframe with additional type column
        :return: None
        """
        columns = ['id', 'chromosome', 'start', 'stop', 'ref', 'alt', 'c_dna', 'protein', 'transcript', 'gene',
                   'consensus_classification'] + self.labs
        consensus_with_type.loc[lambda x: x.type == 'delins'].to_csv(self.delins_file_name, index=False,
                                                                     columns=columns, quoting=csv.QUOTE_NONNUMERIC)

    def write_variant_types(self):
        """
        Writes the output file with the counts for each type of variant per lab and calls function to write delins file
        variants.
        :return: None
        """
        self.consensus_df['type'] = self.consensus_df.apply(lambda x: Variants.get_variant_type(x.ref, x.alt), axis=1)

        classifications = pandas.melt(self.consensus_df, id_vars=['id', 'type'], value_vars=self.labs, var_name="lab",
                                      value_name="classification")

        for lab, lab_classifications in classifications.groupby('lab'):
            self.type_file.write('{}\n'.format(lab.upper()))
            count = lab_classifications.groupby('type').classification.count()
            percentage = count / count.sum() * 100
            for count, percentage in zip(count.iteritems(), percentage.iteritems()):
                self.type_file.write('{:<10}{:<10}{}%\n'.format(count[0], str(count[1]), round(percentage[1], 3)))
            self.type_file.write('\n')

        self.write_delins_file(self.consensus_df)


def main():
    config = ConfigParser('../config/config.txt')
    molgenis_server = molgenis.Session(config.server)
    molgenis_server.login(config.username, config.password)
    csv = config.prefix + 'consensus.csv'
    public = config.prefix + 'public_consensus'
    # Process consensus to fill output
    prefix = config.prefix
    reporter = ConsensusReporter(csv, molgenis_server, config.labs, public, prefix)
    reporter.process_consensus()


if __name__ == '__main__':
    main()
