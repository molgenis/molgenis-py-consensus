from consensus.MolgenisConfigParser import MolgenisConfigParser as ConfigParser


class PreProcessor:
    def __init__(self, lab_files, labs, comments_file, input_dir, output_dir):
        self.output_dir = output_dir
        self.input_dir = input_dir
        self.comments_file = self.create_comments_file(comments_file)
        for lab_file, lab in zip(lab_files, labs):
            self.process_file(lab_file, lab)

        self.comments_file.close()

    @staticmethod
    def _get_id(variant_id, lab):
        prefix = lab.upper().replace('_', '') + '_'
        # Get first 10 of hash
        return prefix + variant_id[0:10]

    @staticmethod
    def _create_comment_line(comment_id):
        return '"{}"\t"-"\n'.format(comment_id)

    def create_comments_file(self, name):
        file_path = self.output_dir + name
        output_file = open(file_path, 'w')
        header = '"id"\t"comments"\n'
        output_file.write(header)
        return output_file

    def process_file(self, file_to_process, lab):
        input_file = open(self.input_dir + file_to_process)
        lab_output_file = open('{}vkgl_{}.tsv'.format(self.output_dir, lab), 'w')
        id_pos = 0
        comments_idx = 0
        for i, line in enumerate(input_file):
            line = line.strip('\n').split('\t')
            if i == 0:
                id_pos = line.index('id')
                comments_idx = line.index('comments')
                del line[comments_idx]
                del line[id_pos]
                line.append('comments\tid\n')
                lab_output_file.write('\t'.join(line))
            else:
                variant_id = line[id_pos]
                lab_variant_id = self._get_id(variant_id, lab)
                del line[comments_idx]
                del line[id_pos]
                # Append it twice, once for comment, once for id
                line.append(lab_variant_id)
                line.append(lab_variant_id)
                lab_output_file.write('\t'.join(line) + '\n')
                self.comments_file.write(self._create_comment_line(lab_variant_id))
        input_file.close()
        lab_output_file.close()


def main(config_file):
    config = ConfigParser(config_file)
    input_folder = config.input
    output_folder = config.output
    labs = config.labs
    prefix = config.prefix
    comments_file = prefix + config.comments + '.tsv'
    lab_files = [prefix + 'export_' + lab + '.tsv' for lab in labs]
    PreProcessor(lab_files, labs, comments_file, input_folder, output_folder)


if __name__ == '__main__':
    main('config/config.txt')
