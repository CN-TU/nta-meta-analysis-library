import argparse
from ntarcpy import database as db


description = """
Gets conferences of papers.
"""


parser = argparse.ArgumentParser(description=description)
parser.add_argument('database', type=str, help="Path to the database directory.")


if __name__ == '__main__':
    args = parser.parse_args()

    confs = {}

    for i, paper in enumerate(db.iterate_directory(args.database)):
        if paper.metadata.conference is not None:
            name = paper.metadata.conference.name
        elif paper.metadata.journal is not None:
            name = paper.metadata.journal.name
        else:
            continue
        if name in confs:
            confs[name] += 1
        else:
            confs[name] = 1

        if i > 500:
            break

    for c, count in sorted(confs.items(), key=lambda x: x[1], reverse=True):
        print(c, count)
