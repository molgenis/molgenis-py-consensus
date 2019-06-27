import sys
import time
from yaspin import yaspin
from termcolor import cprint


class MolgenisDataUpdater:

    def __init__(self, molgenis_server):
        self.molgenis_server = molgenis_server

    def synchronous_upload(self, file_name, msg, ok_msg='✔'):
        """
        Uploads data from csv file to molgenis table
        :param file_name: name of the file to upload (should be *fully qualified name here*.csv)
        :return: True if Finishes
        """
        response = self.molgenis_server.upload_zip(file_name).split('/')
        run_entity_type = response[-2]
        run_id = response[-1]
        status_info = self.molgenis_server.get_by_id(run_entity_type, run_id)

        with yaspin(text=msg, color='green') as spinner:
            while status_info['status'] == 'RUNNING':
                time.sleep(2)
                status_info = self.molgenis_server.get_by_id(run_entity_type, run_id)

            if status_info['status'] == 'FINISHED':
                spinner.ok(ok_msg)
            else:
                spinner.fail('💥')
                cprint("Error while uploading [{}]: {}".format(file_name, status_info['message']), 'red',
                       attrs=['bold'],
                       file=sys.stderr)

    def delete_data(self, table, msg='Deleting data'):
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