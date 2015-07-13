from elasticsearch import Elasticsearch, exceptions as es_exceptions


def index(text, meta, options):
    es = Elasticsearch()
    document_id = meta.get('filesystem_absolute_path', '')
    try:
        result = es.index(
            index=index,
            doc_type="document",
            id=document_id,
            body=meta
        )
    except es_exceptions.TransportError as es_error:
        print(es_error)
        continue
    print(result)
    document_id = result.get('_id')
    count = 1
    result
    for page in text:
        try:
            result = es.index(
                index=index,
                doc_type="page",
                parent=document_id,
                id="{}_page{}".format(document_id, count),
                body={"content": page}
            )
        except es_exceptions.TransportError as es_error:
            print(es_error)
            continue
        print(result)
        count += 1
