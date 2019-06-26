import progressbar
import sys
from molgenis import client as molgenis
from yaspin import yaspin
from termcolor import colored, cprint
from consensus.DataRetriever import DataRetriever
from consensus.ConsensusTableGenerator import ConsensusTableGenerator
from consensus.MolgenisConfigParser import MolgenisConfigParser as ConfigParser
from consensus.HistorySorter import HistorySorter
from consensus.ConsensusReporter import ConsensusReporter


class ConsensusTableUpdater:
    """The ConsensusTableUpdater uploads consensus and consensus comments by first creating a csv file for them"""

    def __init__(self, data, tables, molgenis_server):
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
        self.molgenis_server = molgenis_server
        consensus_table = tables['consensus_table']
        comments_table = tables['comments_table']
        consensus_data = data['consensus_data']
        lab_classifications = data['lab_classifications']
        self.history = data['history']
        self.consensus_table = consensus_table
        self.comments_table = comments_table
        self.delete_consensus()
        self.delete_comments()
        self.upload_comments(consensus_data)
        file_name = self.produce_consensus_csv(consensus_data, lab_classifications)
        self.upload_consensus(file_name, len(consensus_data))

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
        class_map = {'lb': 'Likely benign', 'b': 'Benign', 'lp': 'Likely pathogenic', 'p': 'Pathogenic', 'vus': 'VUS'}

        if variant_classifications[lab] == empty:
            return ',"{}","{}"'.format(empty, empty), False
        else:
            classification = class_map[variant_classifications[lab]]
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

    def delete_comments(self):
        self._delete_data(self.comments_table, 'Deleting old comments')

    def delete_consensus(self):
        self._delete_data(self.consensus_table, 'Deleting old consensus')

    def _delete_data(self, table, msg='Deleting data'):
        """
        Deletes all data from a table using the molgenis client
        :param msg: message showing when busy deleting table
        :param table: fully qualified name of table to delete data from
        :return: None
        """
        with yaspin(text=msg, color='green') as spinner:
            try:
                self.molgenis_server.delete(table)
                spinner.ok('✔')
            except Exception as e:
                spinner.fail('💥')
                cprint("Error while deleting data from [{}]: {}".format(table, e), 'red', attrs=['bold'],
                       file=sys.stderr)

    def _upload_file(self, file_name):
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

        while status_info['status'] == 'RUNNING':
            status_info = self.molgenis_server.get_by_id(run_entity_type, run_id)

        if status_info['status'] == 'FINISHED':
            return True
        else:
            raise ImportError(status_info['message'])

    def upload_comments(self, consensus_data):
        """
        Creates csv for comments and uploads it
        :param consensus_data: dictionary with variant ids (chr_pos_ref_alt_gene) as key
        :return: None
        """
        comments_file_name = self.comments_table + '.csv'

        print('\nUploading comments')

        # Comments have as id the id of the variant and by default the value is "-"
        comments = ['"{}","-"\n'.format(variant) for variant in consensus_data]

        progress = 0

        # Reserve 100 for the last step (uploading the file to molgenis)
        progress_bar = progressbar.ProgressBar(max_value=len(comments) + 100)

        # Open comments file and add header
        comments_file = open(comments_file_name, 'w')
        comments_file.write('"id","comments"\n')

        # Add comments to comments file
        for comment in comments:
            comments_file.write(comment)
            progress += 1
            progress_bar.update(progress)

        comments_file.close()

        done_uploading = self._upload_file(comments_file_name)

        if done_uploading:
            progress += 100
            progress_bar.update(progress)

        progress_bar.finish()

    def upload_consensus(self, file_name, consensus_len):
        """
        Upload consensus table
        :param file_name: name of the file to upload
        :param consensus_len: the number of all unique variants in the consensus table
        :return: None
        """
        with yaspin(text='Uploading consensus table', color='green') as spinner:
            try:
                done_uploading = self._upload_file(file_name)
                if done_uploading:
                    spinner.ok('✔')
                    print('Done uploading [{}] entries of file [{}]'.format(colored(consensus_len, 'blue'),
                                                                            colored(file_name, 'blue')))
            except Exception as e:
                spinner.fail('💥')
                cprint("Error while uploading data of [{}]: {}".format(file_name, e), 'red', attrs=['bold'],
                       file=sys.stderr)

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

    def produce_consensus_csv(self, consensus_data, lab_classifications):
        """
        Produce a csv file with all consensus table data, each line representing a variant
        :param consensus_data:
        :param lab_classifications:
        :return: name of the file
        """
        # Initiate output file
        file_name = self.consensus_table + '.csv'
        output = open(file_name, 'w')

        print('\nWriting consensus table to [{}]'.format(colored(file_name, 'blue')))

        # Start progressbar
        progress_bar = progressbar.ProgressBar(max_value=len(consensus_data))
        progress = 0

        # Create header
        labs = next(iter(lab_classifications.values()))
        header = self.create_consensus_header(labs)
        output.write(header)

        for variant_id in consensus_data:
            variant_lab_classifications = lab_classifications[variant_id]
            line = self.create_consensus_line(variant_id, consensus_data[variant_id], variant_lab_classifications, labs)

            output.write(line)
            progress += 1
            progress_bar.update(progress)

        output.close()
        progress_bar.finish()
        return file_name


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
    data = DataRetriever(config.labs, config.prefix, molgenis_server, history_table).retrieve_all_data()
    lab_data = data.all_lab_data

    # Sort history on export
    history = data.history
    sorted_history = HistorySorter(history, previous_exports).sorted_history

    # Generate consensus table in memory
    consensus_generator = ConsensusTableGenerator(lab_data)
    consensus = consensus_generator.process_variants()
    lab_classifications = consensus_generator.all_lab_classifications

    # Generate and upload CSV with consensus table
    ConsensusTableUpdater(
        data={'consensus_data': consensus, 'lab_classifications': lab_classifications, 'history': sorted_history},
        molgenis_server=molgenis_server,
        tables={'consensus_table': consensus_table, 'comments_table': comments_table})

    # Generate reports
    prefix = config.prefix
    csv = prefix + 'consensus.csv'
    public = prefix + 'public_consensus'
    ConsensusReporter(csv, molgenis_server, config.labs, public).process_consensus()

    molgenis_server.logout()


if __name__ == '__main__':
    main()
