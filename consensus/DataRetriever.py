from molgenis import client as molgenis
import threading, math, progressbar
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
        self.entries_in_batch = 10000
        self.all_lab_data = {}
        self.history = []
        self.prefix = prefix
        total_steps = int(
            sum([self._get_number_of_retrieval_steps(self.get_max_start_pos(prefix + lab)) for lab in labs]))
        total_steps += int(self._get_number_of_retrieval_steps(self.get_max_start_pos(prefix + history)))
        self.progress_bar = progressbar.ProgressBar(max_value=total_steps)
        self.progress = 0
        self.retrieve_data(labs, history)
        self.progress_bar.finish()

    def retrieve_data(self, labs, history):
        """
        Retrieves lab data multi threaded (a thread per lab to make sure the data of each thread is separated properly)
        :param labs: a list with the id's of the labs
        :return: None
        """
        print('Retrieving lab and history data')
        threads = [self.start_thread_for_lab(lab) for lab in labs]
        history_thread = threading.Thread(target=self.start_data_retrieval_for_history, args=(history,))
        history_thread.start()
        threads.append(history_thread)
        for thread in threads:
            thread.join()

    def start_data_retrieval(self, table_name):
        """
        Retrieves all data for one specified lab
        :param table_name: the table_name to retrieve data from
        :return: data: the complete dataset
        """
        table = self.prefix + table_name
        max_start = self.get_max_start_pos(table)
        data = self.retrieve_data_recursively(table, max_start)
        return data

    def start_data_retrieval_for_history(self, table_name):
        """
        Retrieves all data for one specified lab
        :param table_name: the table_name to retrieve data from
        :return: None
        """
        history_data = self.start_data_retrieval(table_name)
        self.history = history_data

    def start_data_retrieval_for_lab(self, lab):
        """
        Retrieves all data for one specified lab
        :param lab: the lab to retrieve data from
        :return: None
        """
        lab_data = self.start_data_retrieval(lab)
        self.all_lab_data[lab] = lab_data

    def start_thread_for_lab(self, lab):
        """
        Starts a thread that retrieves data for a single lab
        :param lab: the id of the lab
        :return: the thread
        """
        thread = threading.Thread(target=self.start_data_retrieval_for_lab, args=(lab,))
        thread.start()
        return thread

    def get_max_start_pos(self, lab):
        """
        Get the start position for the last rest API call based on the total number of variants
        :param lab: the id of the lab
        :return: the last start position
        """
        response = self.server.get(lab, num=0, raw=True)
        total = response['total']
        max_start = math.floor(total / self.entries_in_batch) * self.entries_in_batch
        return max_start

    def _get_number_of_retrieval_steps(self, max_start):
        """
        Get the number of rest api calls that are needed, based on the start of the last page and the entries per batch
        :param max_start: the entry to start the last page on
        :return: the total number of rest api calls needed
        """
        return int(max_start / self.entries_in_batch + 1)

    def retrieve_data_recursively(self, table, max_start, data=[], current_start=0):
        """
        Retrieve all variants for a specific lab recursively
        :param lab: the lab id
        :param max_start: the start position of the last page
        :param data: the data that was already retrieved in previous iterations
        :param current_start: the start position of the current page
        :return: the complete dataset containing the variants of all pages for this lab
        """
        if current_start <= max_start:
            response = self.server.get(table, num=self.entries_in_batch, start=current_start)
            current_start += self.entries_in_batch
            data = data + response
            data = self.retrieve_data_recursively(table, max_start, data, current_start)
            self.progress += 1
            self.progress_bar.update(self.progress)
            return data
        else:
            return data


def main():
    config = ConfigParser('config.txt')
    molgenis_server = molgenis.Session(config.server)
    molgenis_server.login(config.username, config.password)
    DataRetriever(config.labs, config.prefix, molgenis_server, config.history)


if __name__ == '__main__':
    main()
