from os.path import join
from json import load
from update.wp2html import site2html, git_update, insert_analytics

REAL_SITE = 'https://bible.srayaa.com'
SITE_ROOT = r'C:\Users\sraya\Documents\GitHub\sites\bible'
WP_ROOT = r'C:\Users\sraya\Documents\LocalWP\bible\app\public'
REFERENCE = join(SITE_ROOT, r'reference_files')
with open(r'data\bible_pages.json', 'r') as f:
    PAGES = load(f)
with open(r'data\replaces.json', 'r') as f:
    REPLACES = load(f)
with open(join(REFERENCE, 'xhtml', 'analytics.xhtml'), 'r', encoding='utf8') as f:
    ANALYTICS = f.read()


if __name__ == '__main__':
    site2html(PAGES, REPLACES, ('https://bible.srayaa.com/references_files/css/main.css',),
              wp_root=WP_ROOT, site_root=SITE_ROOT, wp_content=join(REFERENCE, 'wp-content'),
              wp_includes=join(REFERENCE, 'wp-includes'))
    insert_analytics(PAGES, ANALYTICS)
    git_update(SITE_ROOT)