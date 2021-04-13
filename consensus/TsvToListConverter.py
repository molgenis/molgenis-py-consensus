class TsvToListConverter:
    @staticmethod
    def _determine_columns_from_header(header):
        return {k: v for v, k in enumerate(header)}

    @staticmethod
    def parse(filename):
        """
        Parses a tab separated file with headers and returns a list of dictionaries of the selected columns
        :param filename: name of the file to parse
        :return: list of dictionaries with the columns as key and the value from that column as value
        """
        converted_list = []
        columns = {}
        with open(filename) as f:
            for i, line in enumerate(f.readlines()):
                data = line.strip('\n').replace('"', '').split('\t')
                if i == 0:
                    columns = TsvToListConverter._determine_columns_from_header(data)
                else:
                    converted_list.append(
                        {column: data[columns[column]] for column in columns}
                    )
        return converted_list


def main():
    converted_list = TsvToListConverter.parse('../output/vkgl_nki.tsv')


if __name__ == '__main__':
    main()
