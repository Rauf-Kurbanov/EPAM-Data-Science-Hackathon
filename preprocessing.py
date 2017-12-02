from bs4 import BeautifulSoup


def replace_unescape(text, unescape_dict={'&lt;': '<', '&gt;': '>', '&amp;': '&', '\r': ''}):
    for k, v in unescape_dict.items():
        text = text.replace(k, v)
    for k, v in unescape_dict.items():
        text = text.replace(k, v)
    return text


def delete_tag(text, tags):
    for tag in tags:
        text = text.replace('<{}>'.format(tag), '')
        text = text.replace('</{}>'.format(tag), '')
    return text


def get_text(text, sep='\n', delete_code=True, code_replacer='CODE', tags=['p', 'pre']):
    # Code.
    soup = BeautifulSoup(text, 'lxml')
    if delete_code:
        for i, tag in enumerate(soup.find_all('code')):
            tag.replaceWith(code_replacer.format(i))

    # Main part.
    return sep.join(
        delete_tag(replace_unescape(p_tag.text), tags)
        for p_tag in soup.find_all(tags)
    )