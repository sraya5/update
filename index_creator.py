from xml.etree.ElementTree import Element, tostring, indent
from os.path import isdir, join, exists
from os import scandir, remove, rename


PDF_FILES = 'C:/Users/sraya/Documents/GitHub/The_Completeness_Axiom-PDF'
PREFIX = 'https://sraya5.github.io/The_Completeness_Axiom-PDF'


def create_index(folder: str, prefix='', root=''):
    index = join(root, folder, 'index.html')
    if exists(index):
        remove(index)

    father = Element('a', attrib={'href': join(prefix, '/'.join(folder.split('/')[:-1]))})
    father.text = '..'

    toc = Element('ol')
    for entry in scandir(join(root, folder)):
        if entry.name.find('git') != -1:
            continue
        lst = entry.name.split('#')
        name = lst[-1]
        e = Element('li')
        l = Element('a')
        if isdir(entry):
            l.set('href', join(name, 'index.html'))
        else:
            l.set('href', name)
        l.text = name
        e.append(l)
        toc.append(e)
        # rename(join(folder, entry.name), join(folder, name))

    root = Element('html', attrib={'xmlns': 'http://www.w3.org/1999/xhtml'})
    head = Element('head')
    body = Element('body')
    body.extend((father, toc))
    root.extend((head, body))
    indent(root)
    string = tostring(root, encoding='utf8')

    with open(index, 'wb') as f:
        f.write(string)


def rec_index(folder: str, prefix='', root=''):
    create_index(folder, prefix, root)
    for entry in scandir(join(root, folder)):
        if entry.name.find('git') != -1:
            continue
        elif entry.name == 'desktop.ini':
            remove(entry)
        elif isdir(entry):
            rec_index(join(folder, entry.name), prefix, root)


if __name__ == '__main__':
    rec_index('', PREFIX, PDF_FILES)
