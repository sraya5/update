from os.path import join
from json import load
from update.wp2html import site2html

REAL_SITE = 'https://lyx.srayaa.com'
SITE_ROOT = r'C:\Users\sraya\Documents\GitHub\lyx'
WP_ROOT = r'C:\Users\sraya\Documents\LocalWP\lyx\app\public'
REFERENCES = join(SITE_ROOT, r'references_files')
with open(r'data\lyx_pages.json', 'r') as f:
    PAGES = load(f)
with open(r'data\replaces.json', 'r') as f:
    REPLACES = load(f)


if __name__ == '__main__':
    site2html(PAGES, REPLACES, ('https://lyx.srayaa.com/references_files/css/main.css',),
              wp_root=WP_ROOT, site_root=SITE_ROOT, wp_content=join(REFERENCES, 'wp-content'),
              wp_includes=join(REFERENCES, 'wp-includes'))