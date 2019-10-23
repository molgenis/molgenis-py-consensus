from consensus.MolgenisDataUpdater import MolgenisDataUpdater
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