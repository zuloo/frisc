import os
import re

import requests
from lxml import html

re_nocamel = re.compile('([a-z])([A-Z])')
re_nopunct = re.compile('[.:\-/ ]')


def parse(path, server=None, port=None):
    _server = server or "localhost"
    _port = port or "9998"
    _endpoint = "http://" + _server + ":" + _port

    basename = os.path.basename(path)

    mime_type = get_mime_type(path)

    with open(path, 'rb') as fp:
        response = requests.put(_endpoint+'/tika', data=fp, headers={
            'Content-Type': mime_type,
            'Accept': 'text/html',
            'Content-Disposition': 'attachment; filename={}'.format(basename)})

    if not response.status_code == requests.codes.ok:
        response.raise_for_status()

    dom = html.fromstring(response.text)

    meta_data = {}
    text_data = {}

    for meta_tag in dom.xpath('//meta'):
        field = re_nocamel.sub(
            r'\1_\2', re_nopunct.sub(r'_', meta_tag.get('name'))
        ).lower()
        meta_data[field] = meta_tag.get('content')

    page_nr = 1
    for page in dom.xpath('//div[@class="page"]'):
        text_data['page {}'.format(page_nr)] = page.text_content()
        page_nr += 1

    return (text_data, meta_data)


def get_mime_type(path, server=None, port=None):
    _server = server or "localhost"
    _port = port or "9998"
    _endpoint = "http://" + _server + ":" + _port

    basename = os.path.basename(path)

    with open(path, 'rb') as fp:
        response = requests.put(_endpoint+'/detect/stream', data=fp, headers={
            'Accept': 'text/plain',
            'Content-Disposition': 'attachment; filename={}'.format(basename)})

    if not response.status_code == requests.codes.ok:
        response.raise_for_status()

    return response.text
