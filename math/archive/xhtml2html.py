from bs4 import BeautifulSoup
from os import remove


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
