import threading
import math
import progressbar
from molgenis import client as molgenis
from consensus.MolgenisConfigParser import MolgenisConfigParser as ConfigParser


class DataRetriever:
    """DataRetriever retrieves the data from all lab tables and the history table"""

    def __init__(self, labs, prefix, server, history):
        """
        :param labs: a list with the id's of the labs
        :param prefix: the prefix for all tables names in molgenis
        :param server: the logged in molgenis client
        """
        self.server = server
        self.pagesize = 10000
        self.all_lab_data = {}
        self.history_table = history
        self.labs = labs
        self.history = []
        self.prefix = prefix
        self.progress = 0

    def _get_number_of_pages(self, table):
        """
        Get the number of pages based on the total number of rows in a table and the pagesize
        :param table: the table name
        :return:
        """
        total = self._get_total(table)
        return math.ceil(total / self.pagesize)

    def retrieve_all_data(self):
        """
        Retrieves lab data multi threaded (a thread per lab to make sure the data of each thread is separated properly)
        :return: None
        """
        print('Retrieving lab and history data')

        total_steps = sum([self._get_number_of_pages(self.prefix + lab) for lab in self.labs])
        total_steps += self._get_number_of_pages(self.prefix + self.history_table)
        self.progress_bar = progressbar.ProgressBar(max_value=total_steps)

        threads = [self._start_thread_for_lab(lab) for lab in self.labs]
        history_thread = threading.Thread(target=self._start_data_retrieval, args=(self.history_table, self.history,))
        history_thread.start()
        threads.append(history_thread)

        for thread in threads:
            thread.join()

        self.progress_bar.finish()

    def _start_data_retrieval(self, table_name, save_location):
        """
        Retrieves all data for one specified lab
        :param table_name: the table_name to retrieve data from
        :param save_location: the location to store the data
        """
        save_location = self._retrieve_data(self.prefix + table_name)

    def _start_thread_for_lab(self, lab):
        """
        Starts a thread that retrieves data for a single lab
        :param lab: the id of the lab
        :return: the thread
        """
        self.all_lab_data[lab] = []
        thread = threading.Thread(target=self._start_data_retrieval, args=(lab, self.all_lab_data[lab],))
        thread.start()
        return thread

    def _get_total(self, lab):
        """
        Get the start position for the last rest API call based on the total number of variants
        :param lab: the id of the lab
        :return: the last start position
        """
        response = self.server.get(lab, num=0, raw=True)
        total = response['total']
        return total

    def _retrieve_data(self, table):
        """
        Retrieve all variants for a specific lab recursively
        :param lab: the lab id
        :param max_start: the start position of the last page
        :param data: the data that was already retrieved in previous iterations
        :param current_start: the start position of the current page
        :return: the complete dataset containing the variants of all pages for this lab
        """
        pages = self._get_number_of_pages(table)
        data = []
        for page in range(pages):
            start = page * self.pagesize
            response = self.server.get(table, num=self.pagesize, start=start)
            data = data + response
            self.progress += 1
            self.progress_bar.update(self.progress)
        return data


def main():
    config = ConfigParser('../config/config.txt')
    molgenis_server = molgenis.Session(config.server)
    molgenis_server.login(config.username, config.password)
    DataRetriever(config.labs, config.prefix, molgenis_server, config.history).retrieve_all_data()


if __name__ == '__main__':
    main()
