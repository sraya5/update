from os import remove
from os.path import exists, join
from requests import get
from json import load
from shutil import copy
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


def site2html(pages: dict[str, str], old_site, new_site, css_files=(), js_files=()):
    for url in pages:
        dst = pages[url]
        if exists(dst):
            remove(dst)
        with open(dst, 'w', encoding='utf8') as file:
            src = get(url).text
            src = src.replace(old_site, new_site)
            src = css_and_js(src, css_files, js_files)
            file.write(src)


def wp_content_and_include(wp_root: str, site_root: str):
    for folder in {'wp-content', 'wp-include'}:
        old = join(wp_root)
        new = join(site_root, folder)
        if exists(new):
            remove(new)
        copy(old, new)


PAGES = 'data\\wp2html.json'
OLD_SITE = 'http://math.local'
NEW_SITE = 'https://math.srayaa.com'
CSS_FILES = ('https://math.srayaa.com/css/main.css', )
WP_ROOT =  r'C:\Users\sraya\Documents\math\app\public'
SITE_ROOT = r'C:\Users\sraya\Documents\GitHub\math'


def main():
    with open(PAGES, 'r') as file:
        pages = load(file)
    site2html(pages, OLD_SITE, NEW_SITE, CSS_FILES)
    # wp_content_and_include(WP_ROOT, SITE_ROOT)


if __name__ == '__main__':
    main()
