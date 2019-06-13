import datetime, re, progressbar, sys
from molgenis import client as molgenis
from consensus.MolgenisConfigParser import MolgenisConfigParser as ConfigParser
from yaspin import yaspin
from termcolor import cprint


class ConsensusReporter:
    """ConsensusReporter generates a log file with all opposites and on the bottom the counts in HTML format and a
    public consensus table."""

    def __init__(self, csv, session, labs, public_consensus, test=False):
        self.labs = labs
        report_id = self._get_month_and_year()

        opposites_file_name = 'opposites_report_{}.txt'.format(report_id)
        counts_file_name = 'counts.html'
        type_file_name = 'types.txt'
        vcf_log_name = 'log.txt'

        if test:
            opposites_file_name = 'test.txt'
            counts_file_name = 'test.html'
            type_file_name = 'test_types.txt'
            vcf_log_name = 'test_log.txt'

        # Open output files
        self.type_file = open(type_file_name, 'w')
        self.log = open(vcf_log_name, 'w')
        self.report = open(opposites_file_name, 'w')
        self.counts_html = open(counts_file_name, 'w')
        self.public_consensus_file = self.prepare_public_consensus_file(public_consensus)
        self.public_consensus_table = public_consensus
        self.molgenis_server = session

        self.types = {lab: {'snp': 0, 'del': 0, 'ins': 0, 'delins': 0} for lab in labs}

        # Define count objects
        self.counts = {
            '(Likely) benign': 0,
            'VUS': 0,
            '(Likely) pathogenic': 0,
            'Opposite classifications': 0,
            'Classified by one lab': 0,
            'No consensus': 0
        }
        self.single_counts = {
            'Benign': 0,
            'Likely benign': 0,
            'VUS': 0,
            'Likely pathogenic': 0,
            'Pathogenic': 0
        }

        # Open input file (csv of consensus table)
        self.open_csv = open(csv)
        self.csv_file = self.open_csv.readlines()

    def _upload_public_consensus(self, file_name):
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

    @staticmethod
    def prepare_public_consensus_file(public_consensus):
        """
        Creates a public consensus csv file to upload
        :param public_consensus: the name of the file (without the csv)
        :return: the opened file
        """
        public_consensus = open('{}.csv'.format(public_consensus), 'w')
        header = '"id","label","chromosome","start","stop","ref","alt","c_notation","p_notation","transcript",' \
                 '"gene","support","classification"\n'
        public_consensus.write(header)
        return public_consensus

    def write_public_consensus_line(self, variant, classification, column_map):
        """
        Writes a line in the public consensus file
        :param variant: the variant line from the consensus csv, splitted on ","
        :param classification: the classification of the variant (if specified by one lab its the lab classification,
        otherwise the consensus classification)
        :param column_map: a dictionary with as keys the column names in the csv and as values the index of that column
        in the consensus csv
        :return: None
        """
        chromosome = variant[column_map['chromosome']]
        start = variant[column_map['start']]
        ref = variant[column_map['ref']]
        alt = variant[column_map['alt']]
        stop = variant[column_map['stop']]
        gene = variant[column_map['gene']]

        label = '{}:{} {} {}>{}'.format(chromosome, start, gene, ref, alt)
        variant_id = '{}_{}_{}_{}_{}'.format(chromosome, start, ref, alt, gene)
        template = '"{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}"\n'

        line = template.format(variant_id, label, chromosome, start, stop, ref, alt,
                               variant[column_map['c_dna']],
                               variant[column_map['protein']],
                               variant[column_map['transcript']],
                               gene,
                               variant[column_map['matches']],
                               classification)

        self.public_consensus_file.write(line)

    @staticmethod
    def _get_column_positions(header):
        """
        Parses the header of a file (list) and returns a dict with all header names as key and their positions as value
        :param header: the header of a file splitted on the separator (list)
        :return: a dictionary with the names of the columns as key and their position in the header as value
        """
        return {col: i for i, col in enumerate(header)}

    def count_type(self, variant, column_map):
        """
        Counts the type of variants for validation purposes. Variants with invalid ref and alt notation will be written
        to log file.
        :param variant: one line of the consensus csv, splitted on "," (list), describing a variant
        :param column_map: the dictionary with the position of each column in the consensus csv
        :return: None
        """
        ref = variant[column_map['ref']]
        alt = variant[column_map['alt']]
        variant_type = ''

        if ref == '.':
            variant_type = 'ins'
        elif alt == '.':
            variant_type = 'del'
        elif ref[0:len(ref) - 1] == alt[0:len(alt) - 1]:
            self.log.write('"ref and alt too long",{}'.format(variant))
            variant_type = 'snp'
        elif len(ref) > 1 and len(alt) > 1:
            variant_type = 'delins'
        elif len(ref) == 1 and len(alt) > 1:
            variant_type = 'ins'
            self.log.write('"Incorrect VCF version (ref should be ., and alt without anchor)",{}'.format(variant))
        elif len(alt) == 1 and len(ref) > 1:
            variant_type = 'del'
            self.log.write('"Incorrect VCF version (ref should be without anchor, and alt .)",{}'.format(variant))
        else:
            variant_type = 'snp'

        for lab in self.labs:
            if variant[column_map[lab]] != '':
                self.types[lab][variant_type] += 1

    def process_consensus(self):
        """
        Processes the lines in the consensus csv to generate reports (public consensus, counts and a list of opposites)
        :param csv_file: the opened csv file
        :return: None
        """
        column_map = {}
        current_progress = 0
        print('Producing counts, public consensus and opposites list')
        progress = progressbar.ProgressBar(max_value=len(self.csv_file))
        for i, line in enumerate(self.csv_file):
            if i == 0:
                column_map = self._get_column_positions(line.split('","'))
            else:
                variant = line.split('","')
                self.count_type(variant, column_map)
                classification = variant[column_map['consensus_classification']].replace('"', '')
                self.counts[classification] += 1
                if classification == 'Opposite classifications':
                    self.write_opposites_line(variant, column_map)
                elif classification == 'Classified by one lab':
                    lab_classification = self.get_single_lab_classification(variant, column_map)
                    self.single_counts[lab_classification] += 1
                    lab_classification = self.convert_classification(lab_classification)
                    self.write_public_consensus_line(variant, lab_classification, column_map)
                elif classification != 'No consensus':
                    classification = self.convert_classification(classification)
                    self.write_public_consensus_line(variant, classification, column_map)
                current_progress += 1
                progress.update(current_progress)
        progress.finish()

        self.write_count_output()
        self.write_type_output()

        # Close in and output files
        self.open_csv.close()
        self.public_consensus_file.close()
        self.report.close()
        self.counts_html.close()
        self.type_file.close()

        # Upload public consensus
        self.delete_public_consensus(self.public_consensus_table)
        self._upload_public_consensus(self.public_consensus_table + '.csv')

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
        now = datetime.datetime.now()
        year = str(now.year)
        month = '0' + str(now.month)
        return '{}{}{}{}'.format(year[-2], year[-1], month[-2], month[-1])

    def write_opposites_line(self, variant, column_map):
        """
        Writes a line in the file with opposites
        :param variant: the variant with the opposite classification
        :param column_map: a dictionary with as key all the column headers and as value the positions
        :return:
        """
        classifications = {lab: variant[column_map[lab]] for lab in self.labs if variant[column_map[lab]] != ''}

        self.report.write('{}:{}-{}\tREF:{}\tALT:{}\t({})\n'.format(variant[column_map['chromosome']],
                                                                    variant[column_map['start']],
                                                                    variant[column_map['stop']],
                                                                    variant[column_map['ref']],
                                                                    variant[column_map['alt']],
                                                                    variant[column_map['gene']]))
        for lab in classifications:
            self.report.write('{}: {}\n'.format(lab, classifications[lab]))
        self.report.write('\n')

    def write_count_output(self):
        """
        Writes a HTML file with the consensus counts (how many times classifications were used)
        :return: None
        """
        now = datetime.datetime.now()
        month = now.strftime("%B")
        year = str(now.year)
        self.counts_html.write('<h1>Counts for {} {} export</h1>\n<ul>\n'.format(month, year))

        for count in self.counts:
            if count != 'Classified by one lab':
                self.counts_html.write('\t<li>{}: {}</li>\n'.format(count, self.counts[count]))

        self.counts_html.write('\t<li>Classified by one lab ({}):\n\t\t<ul>\n'.format(
            str(self.counts['Classified by one lab'])))

        for count in self.single_counts:
            self.counts_html.write('\t\t\t<li>{}: {}</li>\n'.format(count, self.single_counts[count]))

        self.counts_html.write('\t\t</ul>\n\t</li>\n</ul>')

    def write_type_output(self):
        """
        Writes the output file with the counts for each type of variant per lab
        :return:
        """
        total_percentages = {'snp': 0, 'del': 0, 'ins': 0, 'delins': 0}
        for lab in self.types:
            self.type_file.write('{}\n'.format(lab.upper()))
            lab_types = self.types[lab]
            total_variants = 0
            for type in lab_types:
                count = lab_types[type]
                self.type_file.write('{}:{}\n'.format(type, count))
                total_variants += count
            self.type_file.write('\nTotal number of variants: {}\n\n'.format(total_variants))
            self.type_file.write('Percentages:\n')
            for type in lab_types:
                count = lab_types[type]
                percentage = count * 100 / total_variants
                total_percentages[type] += percentage
                self.type_file.write('{}:{}%\n'.format(type, round(percentage, 3)))
            self.type_file.write('\n\n')
        self.type_file.write('Average percentages:\n')
        for type in total_percentages:
            self.type_file.write('{}:{}%\n'.format(type, round(total_percentages[type] / len(self.labs), 3)))


def main():
    config = ConfigParser('config.txt')
    molgenis_server = molgenis.Session(config.server)
    molgenis_server.login(config.username, config.password)
    csv = 'vkgl_consensus.csv'
    public = 'vkgl_public_consensus'
    # Process consensus to fill output
    ConsensusReporter(csv, molgenis_server, config.labs, public).process_consensus()


if __name__ == '__main__':
    main()
