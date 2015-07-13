import re
from zipfile import ZipFile
from xml.dom import minidom


re_nocamel = re.compile('([a-z])([A-Z])')
re_nopunct = re.compile('[.:\-/ ]')


def parse(path):
    mime_type = ''
    meta_data = {}
    text_data = {}

    with ZipFile(path) as zf:
        mime_type = zf.read('mimetype').decode('utf-8')
        meta_data['content_type'] = mime_type

        mx = zf.read('meta.xml')
        md = minidom.parseString(mx)

        # get the meta data from meta.xml
        for meta_tag in md.getElementsByTagName('office:meta')[0].childNodes:
            if meta_tag.attributes.length > 0:
                for attr in meta_tag.attributes.keys():
                    field = re_nocamel.sub(
                        r'\1_\2', re_nopunct.sub(r'_', attr)
                    ).lower()
                    meta_data[field] = meta_tag.getAttribute(attr)
            else:
                meta_text = []
                for node in meta_tag.childNodes:
                    if node.nodeType == node.TEXT_NODE:
                        meta_text.append(node.data)
                field = re_nocamel.sub(
                    r'\1_\2', re_nopunct.sub(r'_', meta_tag.nodeName)
                ).lower()
                meta_data[field] = "".join(meta_text)

        cx = zf.read('content.xml')
        cd = minidom.parseString(cx)

        if mime_type == 'application/vnd.oasis.opendocument.text':
            text_data = extract_from_textdocument(cd, meta_data)
        elif mime_type == 'application/vnd.oasis.opendocument.spreadsheet':
            text_data = extract_from_spreadsheet(cd, meta_data)

        # for page in text_data:
        #     print(page)
        # print(meta_data)

    return (text_data, meta_data)


def extract_from_spreadsheet(dom, meta_data):
    content = {}

    for table in dom.getElementsByTagName('table:table'):
        if table.childNodes == 0:
            continue

        table_content = []
        nodes = []

        for cnode in table.childNodes:
            nodes.append(cnode)

        node = nodes.pop()
        while node:
            # collect text, break page if stylename in break_styles
            if node.nodeType == node.TEXT_NODE:
                table_content.append(node.data)
            # collect childnodes to node filo stack
            elif node.childNodes.length > 0:
                for cnode in node.childNodes:
                    nodes.append(cnode)
            # try to get new node, break loop if failed

            try:
                node = nodes.pop()
            except IndexError:
                break

        # collect last (or actually first)  page content
        table_content.reverse()
        content[table.getAttribute('table:name')] = ' '.join(table_content)

    return content


def extract_from_textdocument(dom, meta_data):
    # collect style names that indicate a manual page break
    break_styles = []
    for style in dom.getElementsByTagName('style:paragraph-properties'):
        if style.hasAttribute('fo:break-before') and \
                style.getAttribute('fo:break-before') == 'page':
            break_styles.append(
                style.parentNode.getAttribute('style:name'))

    # init the neccessary variables to walk content recursively
    content = {}
    page = int(meta_data['meta_page_count'])
    page_content = []
    nodes = []
    break_next = False

    node = dom.getElementsByTagName('office:text')[0]
    while node:
        # collect text, break page if stylename in break_styles
        if node.nodeType == node.TEXT_NODE:
            page_content.append(node.data)
            if break_next:
                # reverse content because we are coming back up
                page_content.reverse()
                content['page {}'.format(page)] = ' '.join(page_content)
                page -= 1
                page_content = []
                break_next = False
        else:
            # set to break after next text node
            if node.hasAttribute('text:style-name') and \
                    node.getAttribute('text:style-name') in break_styles:
                break_next = True
            # break here beacause soft break
            elif node.localName == 'soft-page-break':
                page_content.reverse()
                content['page {}'.format(page)] = ' '.join(page_content)
                page -= 1
                page_content = []
            # collect childnodes to node filo stack
            if node.childNodes.length > 0:
                for cnode in node.childNodes:
                    nodes.append(cnode)

        # try to get new node, break loop if failed
        try:
            node = nodes.pop()
        except IndexError:
            break

    # collect last (or actually first)  page content
    page_content.reverse()
    content['page {}'.format(page)] = ' '.join(page_content)

    return content
