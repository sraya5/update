from helper import SITEMAP_XML
from json import dumps

english2hebrew = {}
for e in SITEMAP_XML.iter():
    en_name = e.get('en_name')
    if en_name is not None and en_name != 'none':
        english2hebrew[en_name] = e.get('he_name', '')

string = dumps(english2hebrew, ensure_ascii=False)
with open(r'english2hebrew.json', 'w', encoding='utf8') as f:
    f.write(string)
