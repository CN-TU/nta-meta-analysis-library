import os
import importlib
import json
try:
    import bibtexparser
except ImportError:
    bibtexparser = None
from .entities import Entity


def _paper_class(version):
    version = '.'.join(version.split('.')[:2])  # use only MAJOR.MINOR, ignore rest
    mod = importlib.import_module('ntarcpy._version.' + version.replace('.', '_') + '.v2_processing.structures')
    paper_class = getattr(mod, 'FullPaper')
    return paper_class


class Paper(object):
    def __init__(self, paper_fname):
        self.fname = paper_fname
        with open(self.fname) as fd:
            paper_dict = json.load(fd)

        version = paper_dict['version']
        self.version = '.'.join(version.split('.')[:2])
        self.full_version = version
        self.paper = _paper_class(version)(paper_dict)
        self._metadata = None

    def __repr__(self):
        return os.sep.join(self.fname.split(os.sep)[-2:])

    @property
    def reference(self):
        return self.paper.reference_block

    @property
    def data(self):
        return self.paper.data_block

    @property
    def preprocessing(self):
        return self.paper.preprocessing_block

    @property
    def analysis_method(self):
        return self.paper.analysis_method_block

    @property
    def evaluation(self):
        return self.paper.evaluation_block

    @property
    def result(self):
        return self.paper.result_block

    @property
    def metadata(self):
        if self._metadata is None:
            ref = self.reference
            self._metadata = Entity(ref.title, ref.authors, ref.year)
        return self._metadata

    def get_bibtex(self):
        assert bibtexparser is not None, 'Please install BibtexParser'
        paper_id = str(self.reference.year) + self.fname.split('/')[-1].split('.')[0]
        paper_type = self.reference.bibtex['type']
        publication_key = {
            'peer_reviewed_journal': 'journal',
            'peer_reviewed_conference': 'booktitle',
            'arxiv': 'journal',
            'technical_report': 'institution',
        }[self.reference.publication_type]
        bibtex_dict = {
            'ID': paper_id,
            'ENTRYTYPE': paper_type,
            'year': str(self.reference.year),
            'title': self.reference.title,
            'author': ' and '.join(self.reference.authors),
            publication_key: self.reference.publication_name,
        }
        if self.reference.organization_publishers is not None:
            bibtex_dict['publisher'] = ' and '.join(
                [get_publisher_name(pub) for pub in self.reference.organization_publishers])
        for field, value in self.reference.bibtex.items():
            if field == 'type':  # skip bibtex type
                continue
            bibtex_dict[field] = value


        bibdb = bibtexparser.bibdatabase.BibDatabase()
        bibdb.entries = [bibtex_dict]
        return bibtexparser.dumps(bibdb)


def get_publisher_name(publisher_string):
    publisher_to_name = {
        'ieee': 'IEEE',
        'elsevier': 'Elsevier',
        'acm': 'ACM',
        'springer': 'Springer',
        'wiley': 'Wiley',
        'taylor_&_francis': 'Taylor & Francis',
        'mdpi': 'MDPI',
    }
    try:
        return publisher_to_name[publisher_string]
    except KeyError:
        return publisher_string


def get_base_features(paper):
    preproc = paper.preprocessing_block
    for packet in preproc.packets:
        if packet.features is not None:
            for feat in packet.features.get_base_feature_names():
                yield feat
    for flow in preproc.flows:
        if flow.features is not None:
            for feat in flow.features.get_base_feature_names():
                yield feat
    for flow_aggregation in preproc.flow_aggregations:
        if flow_aggregation.features is not None:
            for feat in flow_aggregation.features.get_base_feature_names():
                yield feat


def get_field(obj, field):
    if isinstance(obj, (str, bool, int, float)):
        yield obj
    elif field is not None:
        s = field.split('.')
        f = s[0]
        next_f = '.'.join(s[1:]) if len(s) > 0 else None

        if isinstance(obj, dict):
            att = obj[f]
        else:
            att = getattr(obj, f)
        if att is not None:
            if isinstance(att, list):
                for a in att:
                    for val in get_field(a, next_f):
                        yield val
            else:
                for val in get_field(att, next_f):
                    yield val
