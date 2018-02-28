import os
from collections import OrderedDict
import json
from .paper import *


def _open_json(filename):
    return json.load(open(filename))


def iterate_directory(directory):
    for year in sorted(os.listdir(directory)):
        for filename in sorted(os.listdir(directory + os.sep + year)):
            if filename[-5:] == '.json':
                yield Paper(_open_json(directory + os.sep + year + os.sep + filename))


def update_counts(iterator, d):
    for item in iterator:
        if item in d:
            d[item] += 1
        else:
            d[item] = 1
    return d


def update_counts_unique(iterator, d):
    """Same as ``update_counts``, but only counts each item once (for each time it is called).
    Useful for counting the number of papers that have something, rather than the number of times something appears."""
    items = set(iterator)
    for i in items:
        if i in d:
            d[i] += 1
        else:
            d[i] = 1
    return d


##############################################
#
# Count things...
#
##############################################


def count_base_features(directory, perpaper=False):
    """Counts the existing base features in the database.
    If ``perpaper`` is ``True``, repeated features in the same paper are only counted once."""
    out = {}
    for paper in iterate_directory(directory):
        it = get_base_features(paper)
        if perpaper:
            update_counts_unique(it, out)
        else:
            update_counts(it, out)
    return out


def count_field(directory, field, perpaper=False):
    """Counts the existing different values in a specific field.
    If ``perpaper is ``True``, repeated values in the same paper are only counted once."""
    out = {}
    for paper in iterate_directory(directory):
        it = get_field(paper, field)
        if perpaper:
            update_counts_unique(it, out)
        else:
            update_counts(it, out)
    return out


##############################################
#
# Get papers with things...
#
##############################################


def _get_papers_per(directory, f):
    out = {}
    for paper in iterate_directory(directory):
        for val in f(paper):
            if val in out:
                out[val].add(paper)
            else:
                out[val] = {paper}
    return out


def get_papers_per_features(directory):
    """Shows for each base feature in the database the papers that use it."""
    return _get_papers_per(directory, get_base_features)


def get_papers_per_field(directory, field):
    """Shows, for each value in a specific field, the papers that use it."""
    return _get_papers_per(directory, lambda paper: get_field(paper, field))
