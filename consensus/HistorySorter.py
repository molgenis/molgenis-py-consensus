class HistorySorter:
    """The HistorySorter sorts the history by export"""

    def __init__(self, history_data, previous_exports):
        """
        :param history_data: the complete content of the history table
        :param previous_exports: a list of ids of previous exports (format: yymm, 1810 is october 2018)
        """
        self.sorted_history = {export: [] for export in previous_exports}
        self.alternative_history = {export: {} for export in previous_exports}
        self.sort_history(history_data)

    def sort_history(self, unsorted_history):
        """
        Store history of each export separately in a dictionary
        :param unsorted_history: the complete history table
        """
        for variant in unsorted_history:
            export = variant['id'].split('_')[0]
            self.sorted_history[export].append(variant['id'])
            if 'c_dna' in variant and 'transcript' in variant and '{}_{}:{}'.format(
                    variant['gene'], variant['transcript'], variant['c_dna']) not in self.alternative_history[export]:
                self.alternative_history[export]['{}_{}:{}'.format(
                    variant['gene'], variant['transcript'], variant['c_dna'])] = variant['id']