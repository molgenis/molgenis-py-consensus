from consensus.MolgenisDataUpdater import MolgenisDataUpdater
from consensus.MolgenisConfigParser import MolgenisConfigParser as ConfigParser
from consensus.DataRetriever import DataRetriever
from consensus.HistorySorter import HistorySorter
from consensus.ConsensusTableGenerator import ConsensusTableGenerator
from consensus.ConsensusReporter import ConsensusReporter
from consensus.ConsensusFileGenerator import ConsensusFileGenerator

from molgenis import client as molgenis
from termcolor import colored

class ConsensusTableUploader:
    def __init__(self, molgenis_server, consensus_file, comments_file):
        self.molgenis = MolgenisDataUpdater(molgenis_server)
        self.comments_file = comments_file
        self.consensus_file = consensus_file
        self.consensus_table = consensus_file.split('.csv')[0]
        self.comments_table = comments_file.split('.csv')[0]

    def cleanup_before_upload(self):
        """
        This function prepares for the upload of the comments and consensus table, it removes the old consensus data
        and after that the old comments
        :return: None
        """
        self.molgenis.delete_data(self.consensus_table, 'Deleting old consensus')
        self.molgenis.delete_data(self.comments_table, 'Deleting old comments')

    def upload_consensus_table(self):
        """
        Uploads consensus table to molgenis
        :return: None
        """
        self.molgenis.synchronous_upload(self.consensus_file, 'Uploading consensus table',
                                         'Done uploading [{}] {} [{}]'.format(colored(len(self.consensus_file), 'blue'),
                                                                              colored('to', 'green'),
                                                                              colored(len(self.consensus_table), 'blue')
                                                                              ))

    def upload_comments_table(self):
        """
        Uploads comments table to molgenis
        :return: None
        """
        self.molgenis.synchronous_upload(self.comments_file, 'Uploading comments')

    def update_consensus(self):
        """
        Removes old data and uploads new consensus data
        :return: None
        """
        self.cleanup_before_upload()
        self.upload_comments_table()
        self.upload_consensus_table()


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
    file_generator = ConsensusFileGenerator(
        data={'consensus_data': consensus, 'lab_classifications': lab_classifications, 'history': sorted_history},
        tables={'consensus_table': consensus_table, 'comments_table': comments_table})
    consensus_file_name, comments_file_name = file_generator.generate_consensus_files()

    # Upload files
    uploader = ConsensusTableUploader(molgenis_server, consensus_file_name, comments_file_name)
    uploader.update_consensus()

    # Generate reports
    prefix = config.prefix
    csv = prefix + 'consensus.csv'
    public = prefix + 'public_consensus'
    ConsensusReporter(csv, molgenis_server, config.labs, public, prefix).process_consensus()

    molgenis_server.logout()


if __name__ == '__main__':
    main()
