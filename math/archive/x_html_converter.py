from bs4 import BeautifulSoup
from lxml import etree, html
from os import remove
import re


def xhtml2html(xhtml_file, output_file, remove_old=False):
    with open(xhtml_file, "r", encoding="utf-8") as file:
        xhtml_str = file.read()

    soup = BeautifulSoup(xhtml_str, "lxml")

    # Remove XML declaration if it exists
    if soup.contents and isinstance(soup.contents[0], str) and soup.contents[0].strip().startswith("<?xml"):
        soup.contents.pop(0)

    # Remove unnecessary attributes like `xmlns`
    if soup.html and "xmlns" in soup.html.attrs:
        del soup.html.attrs["xmlns"]

    # Convert self-closing tags to normal HTML
    html_str = soup.prettify(formatter="html")  # Ensures proper HTML5 formatting

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(html_str)

    if remove_old:
        remove(xhtml_file)


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

    # Write output file as UTF-8
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(xhtml_str)

    if remove_old:
        remove(html_file)
