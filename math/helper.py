def merge_xhtml(tree1, file2_lxml, output_file):
    root1 = tree1.getroot()

    # XHTML namespace
    XHTML_NS = "http://www.w3.org/1999/xhtml"

    # Extract <head> and <body> from file1 and file2
    head1 = root1.find(f".//{{{XHTML_NS}}}head")
    body1 = root1.find(f".//{{{XHTML_NS}}}body")

    head2 = file2_lxml.find(f".//{{{XHTML_NS}}}head")
    body2 = file2_lxml.find(f".//{{{XHTML_NS}}}body")

    # ====== 1. HEAD: Append file2 elements, but replace <title> with file2's ======
    if head1 is not None and head2 is not None:
        title1 = head1.find(f"{{{XHTML_NS}}}title")
        title2 = head2.find(f"{{{XHTML_NS}}}title")

        if title1 is not None:
            head1.remove(title1)  # Remove old title

        if title2 is not None:
            head1.insert(0, title2)  # Insert new title at the beginning

        for elem in head2:
            if elem.tag.endswith("title"):
                continue  # Skip title because we handled it
            head1.append(elem)  # Append everything else

    # ====== 2. BODY: Insert file2's content before <footer> in file1 ======
    if body1 is not None and body2 is not None:
        footer = body1.find(f".//{{{XHTML_NS}}}footer")  # Find footer

        if footer is not None:
            parent = footer.getparent()
            if parent is not None:
                index = parent.index(footer)  # Get correct insertion index
                for elem in reversed(body2):  # Reverse to preserve order
                    parent.insert(index, elem)
        else:
            for elem in body2:
                body1.append(elem)

    # Save merged XHTML
    tree1.write(output_file, encoding="utf-8", xml_declaration=True, pretty_print=True)


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
