import re
from optparse import OptionParser

from elasticsearch import exceptions as es_exceptions

from parser import TikaParser, FsMetaParser, TextParser, OpenDocumentParser
from index import IndicesManager
from util import get_elasticsearch


available_parser = {}

re_nopunct = re.compile('[.:\-/\\ ]')
parser = OptionParser()

parser.add_option(
    '-I', '--index-files',
    action='store_true', dest='index_mode', default=False,
    help='index all given args')
parser.add_option(
    '-i', '--use-index',
    action='store', type='string', dest='index_name', default='main',
    help='use the following search index')
parser.add_option(
    '-C', '--create-index',
    action='store_true', dest='index_create', default=False,
    help='create a new index')
parser.add_option(
    '-U', '--update-index',
    action='store_true', dest='index_update', default=False,
    help='update an index')
(options, args) = parser.parse_args()


def index_documents(options, args):
    for arg in args:
        mime_type = TikaParser.get_mime_type(arg)

        (text, meta) = TikaParser.parse(arg)

        if not text.keys():
            if 'text/plain' in meta['content_type']:
                (text, txt_meta) = TextParser.parse(arg)
                meta.update(txt_meta)
            elif 'vnd.oasis.opendocument' in meta['content_type']:
                (text, od_meta) = OpenDocumentParser.parse(arg)
                meta.update(od_meta)

        (mpty, fs_meta) = FsMetaParser.parse(arg)
        meta.update(fs_meta)

        meta['content_type'] = mime_type

        for field in meta:
            print("{}: {}".format(field, meta.get(field)))

        # if meta.get('content_type', '') == 'application/pdf':
        #     es_index(text, meta, doctype='pdf', options=options)

        print(text)
        exit()


def add_parser(name, parser):
    available_parser['name'] = parser


def es_index(text, meta, doctype=None, options=None):
    es = get_elasticsearch(options)

    index_name = 'frisc_{}'.format(doctype)
    document_id = meta.get('filesystem_absolute_path', '')
    try:
        result = es.index(
            index=index_name,
            doc_type="{}_doc".format(doctype),
            id=document_id,
            body=meta
        )
    except es_exceptions.TransportError as es_error:
        print(es_error)
        return

    print(result)

    document_id = result.get('_id')
    count = 1
    result
    for page in text:
        try:
            result = es.index(
                index=index_name,
                doc_type="{}_page".format(doctype),
                parent=document_id,
                id="{}_page{}".format(document_id, count),
                body={"content": page}
            )
        except es_exceptions.TransportError as es_error:
            print(es_error)
            continue
        print(result)
        count += 1


if __name__ == "__main__":

    if options.index_create:
        im = IndicesManager()
        res = im.create(options.index_name)
        exit()

    if options.index_update:
        im = IndicesManager()
        im.update(options.index_name)
        exit()

    if options.index_mode:
        res = index_documents(options, args)
        exit()
