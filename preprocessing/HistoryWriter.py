import datetime
from consensus.MolgenisConfigParser import MolgenisConfigParser as ConfigParser


class HistoryWriter:
    def __init__(self, yymm, consensus_file, comments_file, history_file):
        print('We are writing history here!')
        self.yymm = yymm
        self.comments = self.parse_comments_file(comments_file)
        self.parse_consensus_file(consensus_file, history_file)

    @staticmethod
    def parse_comments_file(comments_file):
        opened_file = open(comments_file)
        headers = []
        comments = {}
        for i, line in enumerate(opened_file):
            line = line.strip('\n').replace('"', '').split('\t')
            if i == 0:
                headers = line
            else:
                comments[line[headers.index('id')]] = line[headers.index('comments')]
        opened_file.close()
        return comments

    @staticmethod
    def _remove_column(column):
        return column.endswith('link') or column == 'history'

    def _get_export_moment(self):
        yymm = str(self.yymm)
        year = '20' + yymm[0:2]
        month = datetime.date(1900, int(yymm[2:4]), 1).strftime('%B')
        return '{} {}\n'.format(month, year)

    def parse_consensus_file(self, consensus_file, history_file_name):
        history_file = open(history_file_name, 'w')
        opened_file = open(consensus_file)
        id_pos = 0
        remove_pos = []
        comments_pos = 0
        for i, line in enumerate(opened_file):
            line = line.strip('\n').replace('"', '').split('\t')
            if i == 0:
                id_pos = line.index('id')
                comments_pos = line.index('comments')
                remove_pos = [line.index(link) for link in line if self._remove_column(link)]
                headers = [column for column in line if not self._remove_column(column)]
                headers.append('export\n')
                history_file.write('\t'.join(headers))
            else:
                # move comments value to comments column
                line[comments_pos] = self.comments[line[id_pos]]
                # rename id
                line[id_pos] = '{}_{}'.format(self.yymm, line[id_pos])
                # remove lab link + history columns
                for link_idx in remove_pos[::-1]:
                    del line[link_idx]
                # add export column
                line.append(self._get_export_moment())
                history_file.write('\t'.join(line))

        history_file.close()


def main():
    config = ConfigParser('../config/config.txt')
    input_folder = config.input
    output_folder = config.output
    previous = config.previous[-1]
    HistoryWriter(previous, input_folder + 'vkgl_consensus20{}.tsv'.format(previous),
                            input_folder + 'vkgl_consensus_comments20{}.tsv'.format(previous),
                            output_folder + '/vkgl_consensus_history.tsv')


if __name__ == '__main__':
    main()
