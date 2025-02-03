from os import remove
from os.path import exists
from requests import get
from xml.etree.ElementTree import Element, tostring


def create_css(path: str):
    attrib = {'rel': 'stylesheet', 'type': 'text/css', 'href': path}
    return Element('link', attrib=attrib)


def create_script(source: str, async_=''):
    attrib = {'src': source}
    if async_:
        attrib['async'] = async_
    return Element('script', attrib=attrib)


def css_and_js(html_code, css_files=(), js_files=()):
    css_code = ''
    for path in css_files:
        css_code += tostring(create_css(path), encoding='unicode') + '\n'
    js_code = ''
    for path in js_files:
        js_code += tostring(create_script(path), encoding='unicode') + '\n'
    html_code = html_code.replace('</head>', css_code + js_code + '</head>')
    return html_code


def site2html(pages: dict[str, str], replaces: dict[str, str], css_files=(), js_files=()):
    for url in pages:
        dst = pages[url]
        if exists(dst):
            remove(dst)
        with open(dst, 'w', encoding='utf8') as file:
            src = get(url).text
            for old in replaces:
                src = src.replace(old, replaces[old])
            src = css_and_js(src, css_files, js_files)
            file.write(src)
        print(url)
