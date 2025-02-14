from xml.etree.ElementTree import Element, tostring, fromstring
from lxml import etree, html
import re
from os.path import isfile, isdir, split, join, exists, splitext
from os import scandir, remove

REAL_SITE = 'https://math.srayaa.com'
SITE_ROOT = r'C:\Users\sraya\Documents\GitHub\math'
WP_ROOT = r'C:\Users\sraya\Documents\LocalWP\math\app\public'
REFERENCES = join(SITE_ROOT, r'references_files')
with open(join(REFERENCES, 'xml', 'sitemap.xml'), 'r', encoding='utf8') as f:
    SITEMAP_XML = fromstring(f.read())


def merge_xhtml(root1: Element, root2: Element, output_file: str, toc: Element):
    root1.set('xmlns', 'http://www.w3.org/1999/xhtml')

    head1 = root1[0]
    head2 = root2[0]
    title1 = head1.find('title')
    title2 = head2.find('title')
    title_display = root1.findall(".//*[@id='title_display']")[0]
    if title2 is not None:
        if title1 is not None:
            head1.remove(title1)  # Remove old title
        head1.insert(0, title2)  # Insert new title at the beginning
        title_display.text = title2.text

    for elem in head2:
        if elem.tag.endswith('title'):
            continue  # Skip title because we handled it
        head1.append(elem)  # Append everything else

    toc_container = root1.findall(".//*[@id='toc_container']")[0]
    toc_container.append(toc)

    content_column = root1.findall(".//*[@id='content_column']")[0]
    body2 = root2[1]
    for elem in body2:
        content_column.append(elem)

    name = splitext(split(output_file)[1])[0]
    for screen in {'desktop'}:
        pdf_link = root1.findall(f".//*[@id='pdf_logo_{screen}']")[0][0]
        pdf_link.set('href', f'../{name}.pdf')
        lyx_link = root1.findall(f".//*[@id='lyx_logo_{screen}']")[0][0]
        lyx_link.set('href', f'../{name}.lyx')

    # Save merged XHTML
    xhtml_bytes = tostring(root1, encoding='utf8')
    with open(output_file, 'wb') as file:
        file.write(xhtml_bytes)


def html2xhtml(html_file, output_file, remove_old=False):
    # Read input HTML file as UTF-8
    with open(html_file, "r", encoding="utf-8") as file:
        html_content = file.read()

    # Remove XML declaration if it exists
    html_content = re.sub(r'<\?xml[^>]+\?>', '', html_content, count=1).strip()

    # Convert the HTML content to a lxml tree, ensuring it correctly handles encoding
    parser = html.HTMLParser(encoding="utf-8")
    tree = html.fromstring(html_content, parser=parser)

    # Convert back to properly formatted XHTML
    xhtml_bytes = etree.tostring(tree, pretty_print=True, method="xml", encoding="utf-8")

    # Decode back to string (ensures Hebrew text remains intact)
    xhtml_str = xhtml_bytes.decode("utf-8")

    # Ensure XML declaration is present
    if not xhtml_str.startswith('<?xml'):
        xhtml_str = '<?xml version="1.0" encoding="UTF-8"?>\n' + xhtml_str

    # Ensure XHTML namespace exists
    if 'xmlns="http://www.w3.org/1999/xhtml"' not in xhtml_str:
        xhtml_str = xhtml_str.replace("<html", '<html xmlns="http://www.w3.org/1999/xhtml"', 1)

    xhtml_str.replace('/>', '/ >')

    # Write output file as UTF-8
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(xhtml_str)

    if remove_old:
        remove(html_file)


def extract_import_path(name: str, root: Element, path: str):
    for sub in root:
        if sub.tag == 'import':
            continue
        cur_name = sub.get('en_name', '')
        new_path = join(path, cur_name)
        if cur_name == name:
            return new_path
        else:
            new_path = extract_import_path(name, sub, new_path)
            if new_path:
                return new_path
    return ''


def create_path(element: Element, path: str, root: Element, root_path: str):
    if element.tag == 'import':
        new_path = extract_import_path(element.get('en_name'), root, root_path)
    else:
        new_path = join(path, element.get('en_name'))

    if element.tag in {'topic', 'introduction', 'appendix', 'import'}:
        new_path += '.xhtml'
    return new_path


def remove_number_sign(path: str):
    path = path.split('\\')
    for i in range(len(path)):
        j = path[i].find('#') + 1
        path[i] = path[i][j:]
    path = '\\'.join(path)
    return path


def index2string(index: dict):
    lst = []
    for name in index:
        if index[name] is False:
            lst.append(name)
        elif type(index[name]) is dict:
            index2string(index[name])
    return '\n'.join(lst)


def dir_play(input_path: str, func, args=(), output_path='', info_print=True, index: dict | None = None):
    if index is None:
        index = {}

    if exists(input_path):
        if isfile(input_path):
            name = split(input_path)[1]
            if output_path:
                result, error = func(input_path, *args, output_path)
            else:
                result, error = func(input_path, *args)
            if result:
                index[name] = True
                if info_print:
                    print(f'\t\t   {name}')
            elif error:
                index[name] = False
        elif isdir(input_path):
            if info_print:
                print(f'\ndirectory: {input_path}')
            index[input_path] = {}
            for entry in scandir(input_path):
                new_output_path = join(output_path, entry.name) if output_path else output_path
                dir_play(join(input_path, entry.name), func, args, new_output_path, info_print, index[input_path])
    else:
        raise FileNotFoundError(f'not found such file or directory: {input_path}')
    return index