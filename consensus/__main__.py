from molgenis import client as molgenis
from consensus.DataRetriever import DataRetriever
from consensus.ConsensusTableGenerator import ConsensusTableGenerator
from consensus.MolgenisConfigParser import MolgenisConfigParser as ConfigParser
from consensus.HistorySorter import HistorySorter
from consensus.ConsensusReporter import ConsensusReporter
from consensus.ConsensusFileGenerator import ConsensusFileGenerator


def main():
    # Get data from config
    config = ConfigParser('config/config.txt') # To run by pressing play in pycharm, use ../config/config.txt
    consensus_table = config.prefix + config.consensus
    comments_table = config.prefix + config.comments
    molgenis_server = molgenis.Session(config.server)
    history_table = config.history
    previous_exports = config.previous
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
    sorted_history = HistorySorter(history, previous_exports).sorted_history

    # Generate consensus table in memory
    consensus_generator = ConsensusTableGenerator(lab_data)
    consensus = consensus_generator.process_variants()
    lab_classifications = consensus_generator.all_lab_classifications

    # Generate and upload CSV with consensus table
    file_generator = ConsensusFileGenerator(
        data={'consensus_data': consensus, 'lab_classifications': lab_classifications, 'history': sorted_history},
        tables={'consensus_table': output + consensus_table, 'comments_table': output + comments_table})
    file_generator.generate_consensus_files()

    # Generate reports
    prefix = config.prefix
    csv = '{}/{}consensus.csv'.format(output, prefix)
    public = prefix + 'public_consensus'
    ConsensusReporter(csv, config.labs, public, prefix, output).process_consensus()


if __name__ == '__main__':
    main()
