from xml.etree.ElementTree import Element, tostring
from lxml import etree, html
import re
from os.path import isfile, isdir, split, join, exists, splitext
from os import scandir, remove


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
    pdf_link = root1.findall(".//*[@id='pdf_logo']")[0][0]
    pdf_link.set('href', f'../{name}.pdf')
    lyx_link = root1.findall(".//*[@id='lyx_logo']")[0][0]
    lyx_link.set('href', f'../{name}.lyx')

    # Save merged XHTML
    xhtml_bytes = tostring(root1, encoding='utf8')
    with open(output_file, 'wb') as f:
        f.write(xhtml_bytes)


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


def dir_play(input_path: str, func, args=('', ), index=None, info_print=True):
    if index is None:
        index = {}

    if exists(input_path):
        if isfile(input_path):
            name = split(input_path)[1]
            result, error = func(input_path, *args)
            if result and info_print:
                print(f'\t\t   {name}')
                index[name] = True
            elif error and info_print:
                index[name] = False
        elif isdir(input_path):
            if info_print:
                print(f'\ndirectory: {input_path}')
            index[input_path] = {}
            output_path = str(args[0])
            for entry in scandir(input_path):
                args = (join(output_path, entry.name), ) + args[1:]
                dir_play(join(input_path, entry.name), func, args, index[input_path], info_print)
    else:
        raise FileNotFoundError(f'not found such file or directory: {input_path}')
    return index