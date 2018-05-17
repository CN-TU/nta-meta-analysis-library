import argparse
from ntarcpy import database as db


description = """
Gets number of citations of each paper.
"""


parser = argparse.ArgumentParser(description=description)
parser.add_argument('database', type=str, help="Path to the database directory.")


if __name__ == '__main__':
    args = parser.parse_args()

    for paper in db.iterate_directory(args.database):
        print(str(paper.metadata.paper.citations).ljust(6), paper)
