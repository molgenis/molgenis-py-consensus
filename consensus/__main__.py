from molgenis import client as molgenis
from consensus.DataRetriever import DataRetriever
from consensus.ConsensusTableGenerator import ConsensusTableGenerator
from consensus.MolgenisConfigParser import MolgenisConfigParser as ConfigParser
from consensus.HistorySorter import HistorySorter
from consensus.ConsensusReporter import ConsensusReporter
from consensus.ConsensusTableUpdater import ConsensusTableUpdater


def main():
    # Get data from config
    config = ConfigParser('config.txt')
    consensus_table = config.prefix + config.consensus
    comments_table = config.prefix + config.comments
    molgenis_server = molgenis.Session(config.server)
    history_table = config.history
    previous_exports = config.previous

    # Login on molgenis server
    molgenis_server.login(config.username, config.password)

    # Retrieve data
    data = DataRetriever(config.labs, config.prefix, molgenis_server, history_table)
    lab_data = data.all_lab_data

    # Sort history on export
    history = data.history
    sorted_history = HistorySorter(history, previous_exports).sorted_history

    # Generate consensus table in memory
    consensus_generator = ConsensusTableGenerator(lab_data)
    consensus = consensus_generator.process_variants()
    lab_classifications = consensus_generator.all_lab_classifications

    # Generate and upload CSV with consensus table
    ConsensusTableUpdater(
        data={'consensus_data': consensus, 'lab_classifications': lab_classifications, 'history': sorted_history},
        molgenis_server=molgenis_server,
        tables={'consensus_table': consensus_table, 'comments_table': comments_table})

    # Generate reports
    csv = 'vkgl_consensus.csv'
    public = 'vkgl_public_consensus'
    ConsensusReporter(csv, molgenis_server, config.labs, public).process_consensus()

    molgenis_server.logout()

if __name__ == '__main__':
    main()