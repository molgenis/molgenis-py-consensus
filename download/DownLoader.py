from consensus.MolgenisConfigParser import MolgenisConfigParser as ConfigParser
from molgenis.client import Session

import argparse
import csv
import getpass


class DownLoader:
    def __init__(self, output_dir, table, args):
        self.output_dir = output_dir
        self.session = Session(args.server)
        self.session.login(args.username, args.password)
        self.create_file(table)

    def create_file(self, table):
        file_path = self.output_dir + table + ".tsv"
        print(f"\nGet {table} data")
        data = self.get_data(table)
        meta_attributes = [
            attr["data"]["name"] for attr in
            self.session.get_meta(entity_type_id=table)["attributes"]["items"]
        ]
        print(f"Write output to {file_path}")
        with open(
                file_path,
                "w", encoding="utf-8") as fp:
            writer = csv.DictWriter(
                fp, fieldnames=meta_attributes, delimiter='\t',
                extrasaction="ignore"
            )
            writer.writeheader()
            for row in data:
                for key, value in row.items():
                    if isinstance(value, list):
                        row[key] = ",".join(value)
                writer.writerow(row)

    def get_data(self, table):
        return self.session.get(table, batch_size=10000, uploadable=True)


def main(config_file):
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server', dest='server',
                        help='URL of the MOLGENIS server to download data from')
    parser.add_argument('-u', '--username', dest='username',
                        help='Username for the MOLGENIS server')
    parser.add_argument('-t', '--table(s)', dest='tables',
                        help='One or more tables (comma separated) to be downloaded')
    args = parser.parse_args()
    if args.username is None or args.server is None or args.tables is None:
        raise SystemExit('Must specify username (-u), server (-s) and table(s) (-t)')
    args.password = getpass.getpass(prompt="Enter the password of the server: ")

    config = ConfigParser(config_file)
    input_folder = config.input

    for table in args.tables.split(","):
        DownLoader(input_folder, table, args)


if __name__ == '__main__':
    main('config/config.txt')
