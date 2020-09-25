from molgenis import client as molgenis
from termcolor import colored

from consensus.DataRetriever import DataRetriever
from consensus.ConsensusTableGenerator import ConsensusTableGenerator
from consensus.MolgenisConfigParser import MolgenisConfigParser as ConfigParser
from consensus.HistorySorter import HistorySorter
from consensus.ConsensusReporter import ConsensusReporter
from consensus.ConsensusFileGenerator import ConsensusFileGenerator


def main():
    # Get data from config
    config = ConfigParser('config/config.txt')  # To run by pressing play in pycharm, use ../config/config.txt
    consensus_table = config.prefix + config.consensus
    comments_table = config.prefix + config.comments
    molgenis_server = molgenis.Session(config.server)
    history_table = config.history
    previous_exports = config.previous
    if type(previous_exports) != list:
        previous_exports = [previous_exports]
    output = config.output

    # Login on molgenis server
    molgenis_server.login(config.username, config.password)

    # Retrieve data
    retriever = DataRetriever(config.labs, config.prefix, molgenis_server, history_table)
    retriever.retrieve_all_data()
    lab_data = retriever.all_lab_data
    molgenis_server.logout()

    # Sort history on export
    history = retriever.history
    history_sorter = HistorySorter(history, previous_exports)
    sorted_history = history_sorter.sorted_history
    alternative_history = history_sorter.alternative_history

    # Generate consensus table in memory
    consensus_generator = ConsensusTableGenerator(lab_data)
    consensus = consensus_generator.process_variants()
    lab_classifications = consensus_generator.all_lab_classifications

    # Generate and upload CSV with consensus table
    file_generator = ConsensusFileGenerator(
        data={'consensus_data': consensus, 'lab_classifications': lab_classifications,
              'history': {'history': sorted_history, 'alternative': alternative_history}},
        tables={'consensus_table': output + consensus_table, 'comments_table': output + comments_table},
        incorrect_variant_history_file=output + 'incorrect_variant_history.csv'
    )
    file_generator.generate_consensus_files()

    # Generate reports
    prefix = config.prefix
    csv = '{}/{}consensus.csv'.format(output, prefix)
    public = prefix + 'public_consensus'
    ConsensusReporter(csv, config.labs, public, prefix, output).process_consensus()
    print('Added incorrect variants in history to [{}]'.format(
        colored('{}incorrect_variant_history.csv'.format(output), 'blue')))


if __name__ == '__main__':
    main()
