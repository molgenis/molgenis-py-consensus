import progressbar
from molgenis import client as molgenis
from termcolor import colored
from consensus.DataRetriever import DataRetriever
from consensus.ConsensusTableGenerator import ConsensusTableGenerator
from consensus.MolgenisConfigParser import MolgenisConfigParser as ConfigParser
from consensus.HistorySorter import HistorySorter
from consensus.ConsensusReporter import ConsensusReporter
from consensus.Classifications import Classifications


class ConsensusFileGenerator:
    """The ConsensusTableUpdater uploads consensus and consensus comments by first creating a csv file for them"""

    def __init__(self, data, tables):
        """
        :param data: a dictionary with:
            - consensus_data: variant information as created by process_variants in ConsensusTableGenerator
            - lab_classifications: all lab classifications as all_lab_classifications in ConsensusTableGenerator
            - history: the history data
        :param tables: a dictionary with:
            - consensus_table: the fully qualified name of the consensus table
            - comments_table: the fully qualified name of the consensus comments table
        :param previous_exports: the id of the previous exports (format yymm, for instance: 1810)
        :param molgenis_server: logged in molgenis client
        """
        consensus_table = tables['consensus_table']
        comments_table = tables['comments_table']
        self.consensus_data = data['consensus_data']
        self.lab_classifications = data['lab_classifications']
        self.history = data['history']
        self.consensus_table = consensus_table
        self.comments_table = comments_table

    @staticmethod
    def create_consensus_header(labs):
        """
        Return the header for the consensus csv file
        :param labs: a list with all labs
        :return: the line with the header
        """
        line = '"id","chromosome","start","stop","ref","alt","gene","c_dna","transcript","protein",' \
               '"consensus_classification"'
        for lab in labs:
            line += ',"{}_link","{}"'.format(lab, lab)

        line += ',"matches","history","disease","comments"\n'
        return line

    @staticmethod
    def add_simple_column(line, variant, column):
        """
        Add value as column in csv format
        :param line: the line to add the value to
        :param variant: the variant in which the column is specified
        :param column: the name of the column
        :return: the line after the column is added
        """
        value = variant[column] if column in variant else ''
        line += ',"{}"'.format(value)
        return line

    @staticmethod
    def get_lab_classification(variant_classifications, lab, variant):
        """
        Returns the lab classification and the id of the variant in the lab table if the lab classified the variant
        :param variant_classifications: all classifications provided for the variant ({lab: (b|lb|v|lp|p)})
        :param lab: id of the lab
        :param variant: variant to get info from to generate the lab id of
        :return: if classification is specified: the lab id and classification (,"lab_chr_pos_ref_alt_gene","Benign")
        else two empty columns (,"","")
        """
        chromosome = str(variant['chromosome'])
        start = str(variant['start'])
        ref = variant['ref']
        alt = variant['alt']
        gene = variant['gene']
        empty = ''

        if variant_classifications[lab] == empty:
            return ',"{}","{}"'.format(empty, empty), False
        else:
            classification = Classifications.get_full_classification_from_abbreviation(variant_classifications[lab])
            lab_id = lab.upper().replace('_', '')
            variant_lab_id = lab_id + '_' + chromosome + '_' + start + '_' + ref + '_' + alt + '_' + gene
            return ',"{}","{}"'.format(variant_lab_id, classification), True

    @staticmethod
    def get_match_count_if_consensus(matches, classification):
        """
        Returns the number of labs that classified the variant if they reached consensus
        :param matches: number of labs that classified the variant
        :param classification: the consensus classification
        :return: if consensus classification: the number of labs that agree upon it, else an empty column
        """
        # Consensus can be (Likely) benign/(Likely) pathogenic/VUS and one lab always agrees with itself
        if '(Likely)' in classification or classification == 'VUS' or classification == 'Classified by one lab':
            return ',"{}"'.format(str(matches))
        else:
            return ',""'

    def get_matching_history(self, variant):
        """
        Get the history for the selected variant
        :param variant: de id of the variant to retrieve history from
        :return: a list of ids with history of the variant
        """
        variant_history = []
        for export_id in self.history:
            export = self.history[export_id]
            history_id = export_id + '_' + variant
            if history_id in export:
                variant_history.append(history_id)
            if history_id + '_dup0' in export:
                variant_history.append(history_id + '_dup0')
            if history_id + '_dup1' in export:
                variant_history.append(history_id + '_dup1')
        return variant_history

    def create_consensus_line(self, variant_id, variant, variant_lab_classifications, labs):
        """
        Create a line for one variant in the consensus table
        :param variant_id: id of the variant in this format: chr_pos_ref_alt_gene
        :param variant: one variant from consensus_data as passed to this object
        :param variant_lab_classifications: lab_classifications in the scope of one variant
        :param labs: a list with all labs in it (may be lowercase)
        :return: a line in csv format representing the specific variant
        """
        line = '"{}"'.format(variant_id)
        # Straight forward columns that don't need a transformation
        simple_columns = ['chromosome', 'start', 'stop', 'ref', 'alt', 'gene', 'c_dna', 'transcript', 'protein',
                          'consensus_classification']
        # First add the straight forward columns to the line
        for column in simple_columns:
            line = self.add_simple_column(line, variant, column)

        # Add lab classifications if present, count if classification is present
        matches = 0
        for lab in labs:
            lab_class = self.get_lab_classification(variant_lab_classifications, lab, variant)
            # lab_class[1] is True if lab classification was present
            if lab_class[1]:
                matches += 1
            line += lab_class[0]

        classification = variant['consensus_classification']
        line += self.get_match_count_if_consensus(matches, classification)

        history = ','.join(self.get_matching_history(variant_id))
        line += ',"{}"'.format(history)

        # Add disease code (empty for now) and comments (= xref to comments table, so is same as variant_id)
        line += ',"","{}"\n'.format(variant_id)

        return line

    def generate_consensus_files(self):
        """
        Produce a csv file with all consensus table, and a csv file with the comments, each line representing a variant
        :param consensus_data:
        :param lab_classifications:
        :return: tuple with the names of the files (consensus_file, comments_file)
        """
        comments_file_name = self.comments_table + '.csv'
        consensus_file_name = self.consensus_table + '.csv'

        print('\nWriting consensus table to [{}] and comments table to [{}]'.format(
            colored(consensus_file_name, 'blue'),
            colored(comments_file_name, 'blue')))

        # Start progressbar
        progress_bar = progressbar.ProgressBar(max_value=len(self.consensus_data))
        progress = 0

        # Initiate output files
        consensus_file = open(consensus_file_name, 'w')
        comments_file = open(comments_file_name, 'w')

        # Create headers
        labs = next(iter(self.lab_classifications.values()))
        header = self.create_consensus_header(labs)
        consensus_file.write(header)
        comments_file.write('"id","comments"\n')

        for variant_id in self.consensus_data:
            variant_lab_classifications = self.lab_classifications[variant_id]
            line = self.create_consensus_line(variant_id, self.consensus_data[variant_id], variant_lab_classifications,
                                              labs)
            consensus_file.write(line)
            comment = '"{}","-"\n'.format(variant_id)
            comments_file.write(comment)
            progress += 1
            progress_bar.update(progress)

        consensus_file.close()
        progress_bar.finish()
        return consensus_file_name, comments_file_name


def main():
    # Get data from config
    config = ConfigParser('../config/config.txt')
    consensus_table = config.prefix + config.consensus
    comments_table = config.prefix + config.comments
    molgenis_server = molgenis.Session(config.server)
    history_table = config.history
    previous_exports = config.previous

    # Login on molgenis server
    molgenis_server.login(config.username, config.password)

    # Retrieve data
    retriever = DataRetriever(config.labs, config.prefix, molgenis_server, history_table)
    retriever.retrieve_all_data()
    lab_data = retriever.all_lab_data

    # Sort history on export
    history = retriever.history
    sorted_history = HistorySorter(history, previous_exports).sorted_history

    # Generate consensus table in memory
    consensus_generator = ConsensusTableGenerator(lab_data)
    consensus = consensus_generator.process_variants()
    lab_classifications = consensus_generator.all_lab_classifications

    # Generate and upload CSV with consensus table
    fileGenerator = ConsensusFileGenerator(
        data={'consensus_data': consensus, 'lab_classifications': lab_classifications, 'history': sorted_history},
        tables={'consensus_table': consensus_table, 'comments_table': comments_table})
    consensus_file_name, comments_file_name = fileGenerator.generate_consensus_files()

    # Generate reports
    prefix = config.prefix
    csv = prefix + 'consensus.csv'
    public = prefix + 'public_consensus'
    ConsensusReporter(csv, molgenis_server, config.labs, public, prefix).process_consensus()

    molgenis_server.logout()


if __name__ == '__main__':
    main()
