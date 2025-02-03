from json import load
from os.path import join
from update.wp2html import site2html
from update.math.archive.x_html_converter import html2xhtml

PAGES = r'data\math_pages.json'
REPLACES = r'data\replaces.json'
CSS_FILES = ('https://math.srayaa.com/references_files/css/main.css', )
SITE_ROOT = r'C:\Users\sraya\Documents\GitHub\math'
REFERENCES_XHTML = join(SITE_ROOT, r'references_files\xhtml')
TOPIC_INPUT = join(REFERENCES_XHTML, 'topic.html')
TOPIC_OUTPUT = join(REFERENCES_XHTML, 'topic.xhtml')


if __name__ == '__main__':
    with open(PAGES, 'r') as file:
        pages = load(file)
    with open(REPLACES, 'r') as file:
        replaces = load(file)
    site2html(pages, replaces, CSS_FILES)
    html2xhtml(TOPIC_INPUT, TOPIC_OUTPUT, True)