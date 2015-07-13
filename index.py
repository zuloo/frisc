import sys
import re

from elasticsearch import exceptions as es_exceptions
from elasticsearch.client import IndicesClient
from elasticsearch.helpers import reindex

from util import get_elasticsearch


class IndicesManager(object):

    def __init__(self, options=None):
        self.options = options or {}
        self.es = get_elasticsearch(self.options)
        self.esc = IndicesClient(self.es)
        self.conf_dir = sys.path[0]

    def __create__(self, name, config=None, type=None):
        result = None

        try:
            if not config:
                file_name = "{}/config/{}_index.json".format(
                    self.conf_dir, type)
                with open(file_name) as fp:
                    config = fp.read()

            # create the index with version number
            result = self.esc.create(index=name, body=config)

        except es_exceptions.TransportError:
            print("unable to connect to Elasticsearch")

        return result

    def create(self, doc_type):
        alias_name = 'frisc_{}'.format(doc_type)
        index_name = '{}_v1'.format(alias_name)

        try:
            if self.esc.exists_alias(alias_name):
                print('Index {} already existst, updating'.format(alias_name))
                self.update(doc_type)
                return

            self.__create__(index_name, type=doc_type)

            # set an alias to the index
            self.esc.put_alias(index=index_name, name=alias_name)

        except es_exceptions.TransportError:
            print("unable to connect to Elasticsearch")

    def update(self, doc_type):
        alias_name = 'frisc_{}'.format(doc_type)
        index_name = '{}_v1'.format(alias_name),

        try:
            if not self.esc.exists_alias(alias_name):
                self.create(doc_type)
                return

            version_number = 0
            old_index_name = ''

            old_indexes = self.esc.get_alias(name=alias_name)
            for index in old_indexes.keys():
                match = re.search('^({})_v(\d+)$'.format(alias_name), index)
                if match:
                    version = int(match.group(2))
                    if version > version_number:
                        version_number = version
                        old_index_name = match.group(0)

            version_number += 1
            index_name = '{}_v{}'.format(alias_name, version_number)

            if self.esc.exists(index_name):
                # raise soemthing
                raise

            self.__create__(index_name, type=doc_type)

            reindex(self.es, old_index_name, index_name)

            self.esc.update_aliases(
                body={'actions': [
                    {'remove': {'alias': alias_name, 'index': old_index_name}},
                    {'add': {'alias': alias_name, 'index': index_name}}
                ]}
            )

        except es_exceptions.TransportError:
            print("unable to connect to Elasticsearch")
