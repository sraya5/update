from os import remove, rename
from os.path import exists
from xml.etree.ElementTree import Element, tostring, indent
from helper import create_path


def create_list(sitemap_xml: Element, path: str, root: Element, root_path: str) -> Element:
    lst = Element('ul')
    for sub in sitemap_xml:
        if sub.tag == 'figures':
            continue
        new_sub = Element('li')
        new_path = create_path(sub, path, root, root_path)
        if sub.tag not in {'title', 'none', 'course'}:
            link = Element('a')
            link.set('href', new_path)
            link.text = sub.get('he_name')
            if sub.tag == 'branch':
                strong = Element('strong')
                strong.append(link)
                link = strong
                new_sub.set('class', 'has-large-font-size')
            new_sub.append(link)
        elif sub.tag == 'course':
            new_sub.set('class', 'has-medium-font-size')
            strong = Element('strong')
            strong.text = sub.get('he_name')
            new_sub.append(strong)
        elif sub.tag == 'title':
            new_sub.set('class', 'has-medium-font-size')
            new_sub.text = sub.get('he_name')
        elif sub.tag == 'none':
            new_sub.text = sub.get('he_name')
            new_sub.set('class', 'has-custom-1-color')

        if sub.tag == 'branch':
            lst.append(Element('br'))
        lst.append(new_sub)
        if len(sub):
            new_sub.append(create_list(sub, new_path, root, root_path))
    return lst


def paste_list(sitemap_html: str, lst: Element):
    indent(lst)
    lst = tostring(lst, encoding='utf8').decode('utf8')
    lst = lst.replace("<?xml version='1.0' encoding='utf8'?>", '', 1)
    with open(sitemap_html, 'r', encoding='utf8') as old:
        with open(sitemap_html + '_', 'wb') as new:
            line = old.readline()
            while 'id="content_list"' not in line:
                new.write(line.encode('utf8'))
                line = old.readline()
            line = line[:len(line)-len('</div>\n')] + '\n'
            line += lst
            line += '</div>\n'
            new.write(line.encode('utf8'))

            for line in old:
                new.write(line.encode('utf8'))

    if exists(sitemap_html):
        remove(sitemap_html)
    rename(sitemap_html + '_', sitemap_html)
