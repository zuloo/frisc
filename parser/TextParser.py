import chardet
# from frisc import add_parser


def parse(path):
    meta_data = {}
    text_data = {}
    with open(path, 'rb') as fp:
        raw_text = fp.read()
        encoding = chardet.detect(raw_text)
        meta_data['content_encoding'] = encoding.get(
            'encoding', 'utf-8')

        line_nr = 1
        for line in raw_text.decode(meta_data['content_encoding']).split('\n'):
            text_data['line {}'.format(line_nr)] = line
            line_nr += 1

    return (text_data, meta_data)


# add_parser('text/plain', parse)
