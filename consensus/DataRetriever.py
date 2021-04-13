import threading
import progressbar

from consensus.MolgenisConfigParser import MolgenisConfigParser as ConfigParser
from consensus.TsvToListConverter import TsvToListConverter


class DataRetriever:
    """DataRetriever retrieves the data from all lab tables and the history table"""

    def __init__(self, labs, prefix, history, output_folder):
        """
        :param labs: a list with the id's of the labs
        :param prefix: the prefix for all tables names in molgenis
        :param server: the logged in molgenis client
        """
        self.history_file = history
        self.labs = labs
        self.data = {}
        self.all_lab_data = {}
        self.history = []
        self.prefix = prefix
        self.progress = 0
        self.output_folder = output_folder

    @staticmethod
    def _determine_number_of_steps(list_of_files):
        total_number_of_lines = 0
        for filename in list_of_files:
            total_number_of_lines += DataRetriever._get_number_of_lines(filename)
        return total_number_of_lines

    @staticmethod
    def _get_number_of_lines(filename):
        with open(filename) as f:
            return len(f.readlines())

    def retrieve_all_data(self):
        """
        Retrieves lab data multi threaded (a thread per lab to make sure the data of each thread is separated properly)
        :return: None
        """
        print('Retrieving lab and history data')

        list_of_files = [f'{self.output_folder}{self.prefix}{lab}.tsv' for lab in self.labs]
        list_of_files.append(self.history_file)
        total_steps = DataRetriever._determine_number_of_steps(list_of_files)
        self.progress_bar = progressbar.ProgressBar(max_value=total_steps)

        threads = [self._start_thread_for_lab(lab) for lab in self.labs]
        history_thread = threading.Thread(target=self._get_data_for_history, args=(self.history_file,))
        history_thread.start()
        threads.append(history_thread)

        for thread in threads:
            thread.join()

        self.all_lab_data = self.data
        self.progress_bar.finish()

    def _get_data_for_lab(self, lab):
        self.data[lab] = TsvToListConverter.parse(f'{self.output_folder}{self.prefix}{lab}.tsv')
        self.progress += len(self.data[lab]) + 1
        self.progress_bar.update(self.progress)

    def _get_data_for_history(self, history):
        self.history = TsvToListConverter.parse(f'{history}')

    def _start_thread_for_lab(self, lab):
        """
        Starts a thread that retrieves data for a single lab
        :param lab: the id of the lab
        :return: the thread
        """
        thread = threading.Thread(target=self._get_data_for_lab, args=(lab,))
        thread.start()
        return thread


def main():
    config = ConfigParser('../config/config.txt')
    history_file = f'{config.input}{config.prefix}{config.history}.tsv'
    retriever = DataRetriever(config.labs, config.prefix, history_file, config.output)
    retriever.retrieve_all_data()


if __name__ == '__main__':
    main()
