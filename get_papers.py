import argparse
from ntarcpy import database as db


description = """
Gets list of papers that have fulfill a given logical condition.
"""


parser = argparse.ArgumentParser(description=description)
parser.add_argument('database', type=str, help="Path to the database directory.")
parser.add_argument('condition', type=str, help="The condition to evaluate. Needs escaping. "
                                                "Example: \"paper.preprocessing.normalization_type == 'zscore' and "
                                                "paper.analysis_method.supervised_learning\"")
parser.add_argument('-F', '--sep', type=str, default=';',
                    help="Separator to use in the output.")
parser.add_argument('--papers', action='store_true',
                    help="With this option, get the papers that use each value.")


if __name__ == '__main__':
    args = parser.parse_args()

    condition = args.condition
    papers = []
    for paper in db.iterate_directory(args.database):
        if eval(condition):
            papers.append(paper)
    if args.papers:
        print(args.sep.join([str(p) for p in papers]))
    else:
        print(len(papers))
