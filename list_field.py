import argparse
from ntarcpy import database as db


description = """
Gets existing values in the NTARC database for a specific field.
"""


parser = argparse.ArgumentParser(description=description)
parser.add_argument('database', type=str, help="Path to the database directory.")
parser.add_argument('field', type=str, help="The field to inspect. Example: reference.authors.author")
parser.add_argument('--per-paper', action='store_true',
                    help="With this option, each duplicated values in the same paper are counted only once.")
parser.add_argument('--papers', action='store_true',
                    help="With this option, get the papers that use each value.")
parser.add_argument('-F', '--sep', type=str, default=';',
                    help="Separator to use in the output.")


if __name__ == '__main__':
    args = parser.parse_args()
    if args.papers or args.per_paper:
        key = lambda x: len(x[1])
        f = db.get_papers_per_field
    else:
        key = lambda x: x[1]
        f = db.count_field

    for k, v in sorted(f(args.database, args.field).items(), key=key, reverse=True):
        if args.papers:
            print(k, '|'.join(str(vv) for vv in v), sep=args.sep)
        elif args.per_paper:
            print(k, len(v), sep=args.sep)
        else:
            print(k, v, sep=args.sep)
