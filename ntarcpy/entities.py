import sys
import os.path
import time
import logging
import requests
import unicodedata
import json
from .conf import API_KEY, CACHE_DIR, LOG_LEVEL


USE_API = True
if API_KEY is None or len(API_KEY) < 1:
    USE_API = False
if LOG_LEVEL is None or isinstance(LOG_LEVEL, str) and len(LOG_LEVEL) < 1:
    LOG_LEVEL = logging.WARN
CACHE_DIR = os.path.expanduser(CACHE_DIR)

stderr_handler = logging.StreamHandler(stream=sys.stderr)


class BaseEntity(object):
    _url_base = 'https://api.labs.cognitive.microsoft.com/academic/v1.0/evaluate'
    _attrs = None
    _cache_dirname = None

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(LOG_LEVEL)
        self.logger.addHandler(stderr_handler)

        self._data = None
        self.id = None

        self._set_id()

    def _set_id(self):
        """To be implemented by each entity.
        Returns the id of the requested entity."""
        raise NotImplementedError

    @property
    def name(self):
        raise NotImplementedError

    def __repr__(self):
        try:
            return self.name
        except NotImplementedError:
            return type(self).__name__ + '_' + str(self.id)


    def __eq__(self, other):
        return type(self).__name__ == type(other).__name__ and self.id == other.id

    def __hash__(self):
        return hash(str(self))

    @property
    def _cache_id_filename(self):
        return self._get_cache_id_filename()

    def _get_cache_id_filename(self):
        """Returns the filename of the corresponding cached file."""
        assert self._cache_dirname is not None
        dirname = CACHE_DIR + os.sep + self._cache_dirname
        os.makedirs(dirname, exist_ok=True)
        assert self.id is not None
        return dirname + os.sep + str(self.id)

    def _write_cache(self, data):
        try:
            with open(self._cache_id_filename, 'r') as fd:
                old_data = json.load(fd)
                old_data.update(data)
                data = old_data
        except FileNotFoundError:
            pass
        with open(self._cache_id_filename, 'w') as fd:
            json.dump(data, fd)

    def _load_cache(self):
        with open(self._cache_id_filename, 'r') as fd:
            self._data = json.load(fd)

    def _check_cache(self):
        """Checks if cache exists."""
        return os.path.isfile(self._cache_id_filename)

    def _query_id_attrs(self, qid, attrs):
        """Queries the server for the given ``id``, with ``attrs`` the attributes in the request."""
        if not self._check_cache():
            if not USE_API:
                raise IOError('No API key was given in config.py.')
            self.logger.debug('Querying for id: %d' % qid)
            expr = 'Id=' + str(qid)

            url = self._url_base
            url += '?expr=' + expr
            url += '&attributes=' + attrs

            r = requests.get(url, headers={'Ocp-Apim-Subscription-Key': API_KEY})
            data = r.json()
            if self._data is None:
                self._data = {}
            self._data['microsoft_api'] = data['entities'][0]
            self._write_cache(self._data)
            time.sleep(1)
        else:
            self._load_cache()

    @property
    def data(self):
        """Raw content of the queried/cached data."""
        if self._data is None:
            self._query_id_attrs(self.id, self._attrs)
        return self._data


class PaperEntity(BaseEntity):
    _attrs = 'Id,Ti,L,Y,D,CC,ECC,AA.AuN,AA.AuId,AA.AfN,AA.AfId,F.FN,F.FId,J.JN,J.JId,C.CN,C.CId,RId,W,E'
    _cache_dirname = 'paper_id'

    def __init__(self, title, authors, year):
        self.title = title
        self.authors = authors
        self.year = year
        super(PaperEntity, self).__init__()

    def __repr__(self):
        return '; '.join([str(self.authors), self.title, str(self.year)])

    def _set_id(self):
        fname = self._get_id_map_filename()
        if os.path.exists(fname):
            with open(fname, 'r') as fd:
                self.id = int(fd.read())
        else:
            self.id = self._query_id()
            with open(fname, 'w') as fd:
                fd.write(str(self.id))

    def _get_id_map_filename(self):
        dirname = CACHE_DIR + os.sep + 'paper_id_map'
        os.makedirs(dirname, exist_ok=True)
        fname = str(self.year) + self.title.replace('/', '')
        fname = ''.join(fname.split()).lower()
        fname = unicodedata.normalize('NFKD', fname)
        return dirname + os.sep + fname

    def _query_id(self):
        self.logger.debug('Querying for: %s' % str(self))
        title = "Ti='" + ''.join(e if e.isalnum() else ' ' for e in self.title.lower()).replace('  ', ' ').strip() + "'"
        year = "Y=[" + str(self.year - 2) + ',' + str(self.year + 2) + ']'
        expr = "And(" + title + ', ' + year + ')'

        url = self._url_base
        url += '?expr=' + expr
        url += '&attributes=' + self._attrs
        r = requests.get(url, headers={'Ocp-Apim-Subscription-Key': API_KEY})
        data = r.json()

        if 'entities' not in data or len(data['entities']) != 1:
            if 'entities' in data and len(data['entities']) > 1:
                self.logger.warning('Found multiple entries for paper: %s' % str(self))
            else:
                self.logger.warning('Could not find entity for paper: %s' % str(self))
            self.logger.debug('Expression used: %s' % expr)

        if self._data is None:
            self._data = {}
        self._data['microsoft_api'] = data['entities'][0]

        self.id = self._data['microsoft_api']['Id']
        self._write_cache(self._data)
        time.sleep(1)
        return self.id

    @property
    def citations(self):
        return self.data['microsoft_api']['ECC']


class BaseEntityId(BaseEntity):
    """Extends :class:`BaseEntity`, for when the ID is known at init."""
    def __init__(self, entity_id):
        self.entity_id = entity_id
        super(BaseEntityId, self).__init__()

    def _set_id(self):
        self.id = self.entity_id


class AuthorEntity(BaseEntityId):
    _cache_dirname = 'author_id'
    _attrs = 'Id,AuN,DAuN,CC,ECC,E,SSD'

    @property
    def name(self):
        return self.data['microsoft_api']['DAuN']


class AffiliationEntity(BaseEntityId):
    _cache_dirname = 'affiliation_id'
    _attrs = 'Id,AfN,DAfN,CC,ECC,SSD'

    @property
    def name(self):
        return self.data['microsoft_api']['DAfN']


class JournalEntity(BaseEntityId):
    _cache_dirname = 'journal_id'
    _attrs = 'Id,DJN,JN,CC,ECC,SSD'

    @property
    def name(self):
        return self.data['microsoft_api']['JN']

    @property
    def normalized_name(self):
        return self.data['microsoft_api']['DJN']


class ConferenceSeriesEntity(BaseEntityId):
    _cache_dirname = 'conferenceseries_id'
    _attrs = 'Id,CN,DCN,CC,ECC,F.FId,F.FN,SSD'

    @property
    def name(self):
        return self.data['microsoft_api']['DCN']

    @property
    def normalized_name(self):
        return self.data['microsoft_api']['CN']


class ConferenceInstanceEntity(BaseEntityId):
    _cache_dirname = 'conferenceinstance_id'
    _attrs = 'Id,CIN,DCN,CIL,CISD,CIED,CIARD,CISDD,CIFVD,CINDD,CD.T,CD.D,PCS.CN,PCS.CId,CC,ECC,SSD'


class FieldOfStudyEntity(BaseEntityId):
    _cache_dirname = 'fieldofstudy_id'
    _attrs = 'Id,FN,DFN,CC,ECC,FL,FP.FN,FP.FId,SSD'


class Entity(object):
    def __init__(self, title, authors, year):
        self.paper = PaperEntity(title, authors, year)

        data = self.paper.data['microsoft_api']
        self.authors = [AuthorEntity(a['AuId']) for a in data['AA']]
        self.affiliations = [AffiliationEntity(a['AfId']) if 'AfId' in a else None for a in data['AA']]
        self.journal = JournalEntity(data['J']['JId']) if 'J' in data else None
        self.conference = ConferenceSeriesEntity(data['C']['CId']) if 'C' in data else None
        self.fields_of_study = [FieldOfStudyEntity(a['FId']) for a in data['F']]
