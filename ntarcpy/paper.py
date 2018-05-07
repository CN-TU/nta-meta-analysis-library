import importlib


def _paper_class(version):
    if version == 'v2':  # exception for v2 name
        version = 'v2.0'
    mod = importlib.import_module('ntarcpy._version.' + version.replace('.', '_') + '.v2_processing.structures')
    paper_class =  getattr(mod, 'FullPaper')
    return paper_class


def Paper(paper):
    version = paper['version']
    return _paper_class(version)(paper)


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
