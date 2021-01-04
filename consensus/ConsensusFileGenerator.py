import progressbar
from termcolor import colored
from consensus.Hasher import Hasher
from consensus.Classifications import Classifications


class ConsensusFileGenerator:
    """The ConsensusTableUpdater uploads consensus and consensus comments by first creating a csv file for them"""

    def __init__(self, data, tables, incorrect_variant_history_file=None):
        """
        :param data: a dictionary with:
            - consensus_data: variant information as created by process_variants in ConsensusTableGenerator
            - lab_classifications: all lab classifications as all_lab_classifications in ConsensusTableGenerator
            - history: the history data
        :param tables: a dictionary with:
            - consensus_table: outputDir + the fully qualified name of the consensus table
            - comments_table:  outputDir + the fully qualified name of the consensus comments table
        """
        consensus_table = tables['consensus_table']
        comments_table = tables['comments_table']
        self.consensus_data = data['consensus_data']
        self.lab_classifications = data['lab_classifications']
        self.history = data['history']['history']
        self.alternative_history = data['history']['alternative']
        self.consensus_table_file_name = consensus_table
        self.comments_table_file_name = comments_table
        self.incorrect_variant_history_file_name = incorrect_variant_history_file
        if self.incorrect_variant_history_file_name:
            incorrect_history_file = open(self.incorrect_variant_history_file_name, 'w')
            incorrect_history_file.close()

    @staticmethod
    def create_consensus_header(labs):
        """
        Return the header for the consensus csv file
        :param labs: a list with all labs
        :return: the line with the header
        """
        line = '"id","chromosome","start","stop","ref","alt","gene","c_dna","transcript","protein","hgvs",' \
               '"consensus_classification"'
        for lab in labs:
            line += ',"{}_link","{}"'.format(lab, lab)

        line += ',"matches","history","disease","comments"\n'
        return line

    @staticmethod
    def _add_simple_column(line, variant, column):
        """
        Add value as column in csv format
        :param line: the line to add the value to
        :param variant: the variant in which the column is specified
        :param column: the name of the column
        :return: the line after the column is added
        """
        value = variant[column] if column in variant else ''
        line += ',"{}"'.format(value)
        return line

    @staticmethod
    def _get_lab_classification(variant_classifications, lab, variant):
        """
        Returns the lab classification and the id of the variant in the lab table if the lab classified the variant
        :param variant_classifications: all classifications provided for the variant ({lab: (b|lb|v|lp|p)})
        :param lab: id of the lab
        :param variant: variant to get info from to generate the lab id of
        :return: if classification is specified: the lab id and classification (,"lab_chr_pos_ref_alt_gene","Benign")
        else two empty columns (,"","")
        """
        chromosome = str(variant['chromosome'])
        start = str(variant['start'])
        ref = variant['ref']
        alt = variant['alt']
        gene = variant['gene']
        empty = ''

        if variant_classifications[lab] == empty:
            return ',"{}","{}"'.format(empty, empty), False
        else:
            classification = Classifications.get_full_classification_from_abbreviation(variant_classifications[lab])
            lab_id = lab.upper().replace('_', '')
            variant_id = Hasher.hash(chromosome + '_' + start + '_' + ref + '_' + alt + '_' + gene)[0:10]
            variant_lab_id = lab_id + '_' + variant_id
            return ',"{}","{}"'.format(variant_lab_id, classification), True

    @staticmethod
    def _get_match_count_if_consensus(matches, classification):
        """
        Returns the number of labs that classified the variant if they reached consensus
        :param matches: number of labs that classified the variant
        :param classification: the consensus classification
        :return: if consensus classification: the number of labs that agree upon it, else an empty column
        """
        # Consensus can be (Likely) benign/(Likely) pathogenic/VUS and one lab always agrees with itself
        if '(Likely)' in classification or classification == 'VUS' or classification == 'Classified by one lab':
            return ',"{}"'.format(str(matches))
        else:
            return ',""'

    @staticmethod
    def _add_history_of_variant(id_to_match, export, variant_history):
        if id_to_match in export:
            variant_history.append(id_to_match)
        return variant_history

    @staticmethod
    def _get_history_ids_for_variant(variant_id, chromosome, position, ref, alt, gene, variant_type):
        ids = [variant_id]
        # From okt 2019 on, the id's are hashed
        old_id = '{}_{}_{}_{}_{}'.format(chromosome, position, ref, alt, gene)
        ids.append(old_id)
        # This is done for the variants that lack their anchor (before the 2019 okt export)
        if variant_type == "del":
            old_ref = ref[1::]
            old_alt = '.'
            old_pos = int(position) + 1
            old_id_del_ins = '{}_{}_{}_{}_{}'.format(chromosome, old_pos, old_ref, old_alt, gene)
            ids.append(old_id_del_ins)
        elif variant_type == "ins" or variant_type == "dup":
            old_ref = "."
            old_alt = alt[1::]
            old_id_del_ins = '{}_{}_{}_{}_{}'.format(chromosome, position, old_ref, old_alt, gene)
            ids.append(old_id_del_ins)
        elif variant_type == "delins":
            # ids for indels when this was still an issue https://github.com/molgenis/data-transform-vkgl/issues/12
            old_pos = str(int(position) - 1)
            old_ref1 = "A" + ref
            old_alt1 = "A" + alt
            old_id1 = Hasher.hash(chromosome + '_' + old_pos + '_' + old_ref1 + '_' + old_alt1 + '_' + gene)[0:10]
            old_ref2 = "G" + ref
            old_alt2 = "G" + alt
            old_id2 = Hasher.hash(chromosome + '_' + old_pos + '_' + old_ref2 + '_' + old_alt2 + '_' + gene)[0:10]
            old_ref3 = "T" + ref
            old_alt3 = "T" + alt
            old_id3 = Hasher.hash(chromosome + '_' + old_pos + '_' + old_ref3 + '_' + old_alt3 + '_' + gene)[0:10]
            old_ref4 = "C" + ref
            old_alt4 = "C" + alt
            old_id4 = Hasher.hash(chromosome + '_' + old_pos + '_' + old_ref4 + '_' + old_alt4 + '_' + gene)[0:10]
            ids.append(old_id1)
            ids.append(old_id2)
            ids.append(old_id3)
            ids.append(old_id4)

        return ids

    def _get_matching_history(self, variant):
        """
        Get the history for the selected variant
        :param variant: the complete variant to retrieve history from
        :return: a list of ids with history of the variant
        """
        variant_history = []
        variant_id = variant['id']
        ref = variant["ref"]
        alt = variant["alt"]
        start = variant["start"]
        chromosome = variant["chromosome"]
        gene = variant["gene"]
        variant_type = variant['type']
        incorrect_history_file = None
        if self.incorrect_variant_history_file_name:
            incorrect_history_file = open(self.incorrect_variant_history_file_name, 'a')
        ids = self._get_history_ids_for_variant(variant_id, chromosome, start, ref, alt, gene, variant_type)

        for export_id in self.history:
            possible_ids = [export_id + '_' + row_id for row_id in ids]
            export = self.history[export_id]

            for possible_id in possible_ids:
                variant_history = self._add_history_of_variant(possible_id, export, variant_history)
                variant_history = self._add_history_of_variant(possible_id + '_dup0', export, variant_history)
                variant_history = self._add_history_of_variant(possible_id + '_dup1', export, variant_history)

            alternative_history = self.alternative_history[export_id]
            if 'transcript' in variant and 'c_dna' in variant:
                variant_id = self._check_alternative_history(variant['transcript'], variant['c_dna'], gene,
                                                             alternative_history)
                if variant_id and variant_id not in variant_history:
                    variant_history.append(variant_id)
                    message = '{} is invalid; will be replaced by correct variant {}\n'.format(
                        variant_id, variant['id'])
                    if incorrect_history_file:
                        incorrect_history_file.write('{},{}'.format(variant_id, message))

        if incorrect_history_file:
            incorrect_history_file.close()
        return variant_history

    def _create_consensus_line(self, variant_id, variant, variant_lab_classifications, labs):
        """
        Create a line for one variant in the consensus table
        :param variant_id: id of the variant in this format: hash of chr_pos_ref_alt_gene
        :param variant: one variant from consensus_data as passed to this object
        :param variant_lab_classifications: lab_classifications in the scope of one variant
        :param labs: a list with all labs in it (may be lowercase)
        :return: a line in csv format representing the specific variant
        """
        line = '"{}"'.format(variant_id)
        # Straight forward columns that don't need a transformation
        simple_columns = ['chromosome', 'start', 'stop', 'ref', 'alt', 'gene', 'c_dna', 'transcript', 'protein', 'hgvs',
                          'consensus_classification']
        # First add the straight forward columns to the line
        for column in simple_columns:
            line = self._add_simple_column(line, variant, column)

        # Add lab classifications if present, count if classification is present
        matches = 0
        for lab in labs:
            lab_class = self._get_lab_classification(variant_lab_classifications, lab, variant)
            # lab_class[1] is True if lab classification was present
            if lab_class[1]:
                matches += 1
            line += lab_class[0]

        classification = variant['consensus_classification']
        line += self._get_match_count_if_consensus(matches, classification)

        history = ','.join(self._get_matching_history(variant))
        line += ',"{}"'.format(history)

        # Add disease code (empty for now) and comments (= xref to comments table, so is same as variant_id)
        line += ',"","{}"\n'.format(variant_id)

        return line

    def generate_consensus_files(self):
        """
        Produce a csv file with all consensus table, and a csv file with the comments, each line representing a variant
        :param consensus_data:
        :param lab_classifications:
        :return: tuple with the names of the files (consensus_file, comments_file)
        """
        comments_file_name = self.comments_table_file_name + '.csv'
        consensus_file_name = self.consensus_table_file_name + '.csv'

        print('\nWriting consensus table to [{}] and comments table to [{}]'.format(
            colored(consensus_file_name, 'blue'),
            colored(comments_file_name, 'blue')))

        # Start progressbar
        progress_bar = progressbar.ProgressBar(max_value=len(self.consensus_data))
        progress = 0

        # Initiate output files
        consensus_file = open(consensus_file_name, 'w')
        comments_file = open(comments_file_name, 'w')

        # Create headers
        labs = next(iter(self.lab_classifications.values()))
        header = self.create_consensus_header(labs)
        consensus_file.write(header)
        comments_file.write('"id","comments"\n')

        for variant_id in self.consensus_data:
            variant_lab_classifications = self.lab_classifications[variant_id]
            line = self._create_consensus_line(variant_id, self.consensus_data[variant_id], variant_lab_classifications,
                                               labs)
            consensus_file.write(line)
            comment = '"{}","-"\n'.format(variant_id)
            comments_file.write(comment)
            progress += 1
            progress_bar.update(progress)

        consensus_file.close()
        comments_file.close()
        progress_bar.finish()
        return consensus_file_name, comments_file_name

    @staticmethod
    def _check_alternative_history(transcript, c_dna, gene, export):
        variant = '{}_{}:{}'.format(gene, transcript, c_dna)
        if variant in export:
            return export[variant]
