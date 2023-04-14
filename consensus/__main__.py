from termcolor import colored

from consensus.DataRetriever import DataRetriever
from consensus.ConsensusTableGenerator import ConsensusTableGenerator
from consensus.MolgenisConfigParser import MolgenisConfigParser as ConfigParser
from consensus.HistorySorter import HistorySorter
from consensus.ConsensusReporter import ConsensusReporter
from consensus.ConsensusFileGenerator import ConsensusFileGenerator


def main(config_file):
    # Get data from config
    config = ConfigParser(config_file)
    consensus_table = config.prefix + config.consensus
    comments_table = config.prefix + config.consensus + config.comments
    history_file = f'{config.input}{config.prefix}{config.history}.tsv'
    previous_exports = config.previous
    if type(previous_exports) != list:
        previous_exports = [previous_exports]
    output = config.output
    labs = config.labs

    # Retrieve data
    retriever = DataRetriever(labs, config.prefix, history_file, config.output)
    retriever.retrieve_all_data()
    lab_data = retriever.all_lab_data

    # Sort history on export
    history = retriever.history
    history_sorter = HistorySorter(history, previous_exports)
    sorted_history = history_sorter.sorted_history
    alternative_history = history_sorter.alternative_history

    # Generate consensus table in memory
    consensus_generator = ConsensusTableGenerator(lab_data)
    consensus = consensus_generator.process_variants()

    # Generate and upload TSV with consensus table
    file_generator = ConsensusFileGenerator(
        data={'consensus': consensus, 'history': {'history': sorted_history, 'alternative': alternative_history}},
        tables={'consensus_table': output + consensus_table, 'comments_table': output + comments_table},
        labs=labs,
        incorrect_variant_history_file=output + 'incorrect_variant_history.tsv'
    )
    file_generator.generate_consensus_files()

    # Generate reports
    prefix = config.prefix
    tsv = '{}/{}consensus.tsv'.format(output, prefix)
    public = prefix + 'public_consensus'
    ConsensusReporter(tsv, config.labs, public, prefix, output).process_consensus()
    print('Added incorrect variants in history to [{}]'.format(
        colored('{}incorrect_variant_history.tsv'.format(output), 'blue')))


if __name__ == '__main__':
    main('config/config.txt') # To run by pressing play in pycharm, use ../config/config.txt
