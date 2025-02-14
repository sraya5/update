from os import remove, rename
from os.path import join, exists
from copy import deepcopy
from xml.etree.ElementTree import Element, fromstring, tostring, indent
from helper import REFERENCES, create_path

PATH = join(REFERENCES, 'xhtml', 'branch.xhtml')
with open(PATH, 'r', encoding='utf8') as f:
    element = fromstring(f.read())
    column = element.findall(".//*[@id='first_col']")[0]
    indent(column[0])
    string = tostring(column[0], encoding='utf8').decode(encoding='utf8')
    string = string.replace('<html:', '<')
    string = string.replace('</html:', '</')
    COURSE = fromstring(string)


def one_topic(topic: Element, new_path: str, depth: int):
    new_topic = Element('li')

    if depth == 0:
        strong = Element('strong')
        new_topic.append(strong)
        base = strong
    else:
        base = new_topic

    if topic.tag == 'none':
        base.text = topic.get('he_name')
        new_topic.set('class', 'has-custom-1-color')
    elif topic.tag != 'title':
        link = Element('a')
        link.set('href', new_path)
        link.text = topic.get('he_name')
        base.append(link)
    else:
        base.text = topic.get('he_name')

    return new_topic


def create_topics(course: Element, course_data: Element, data_root: Element, root_path: str):
    topics = course.findall('.//*ul')[0]
    topics.clear()
    for topic in course_data:
        path = join(root_path, course_data.get('en_name'))
        new_path = create_path(topic, path, data_root, root_path)
        new_topic = one_topic(topic, new_path, 0)
        topics.append(new_topic)

        if len(topic):
            lst = Element('ul')
            new_topic.append(lst)
            for sub in topic:
                new_sub = one_topic(sub, new_path, 1)
                lst.append(new_sub)



def create_details(course: Element, course_data: Element):
    details = course.findall('.//*p')[0]
    attrib = deepcopy(details.attrib)
    details.clear()
    details.attrib = attrib

    text = ''
    course_number = course_data.get('course_number')
    if course_number is not None and course_number != 'none':
        text += f"מס' קורס: {course_number}" + '\n'
    lecturer = course_data.get('lecturer')
    if lecturer is not None and lecturer != 'none':
        text += f"מרצה: {lecturer}" + '\n'
    tutor = course_data.get('tutor')
    if tutor is not None and tutor != 'none':
        text += f"מתרגל: {tutor}" + '\n'
    semester = course_data.get('semester')
    if tutor is not None and tutor != 'none':
        text += f"סמסטר {semester}" + '\n'
    if text:
        text += 'האוניברסיטה העברית'
    text = text.splitlines()
    if text:
        details.text = text[0]
    for t in text[1:]:
        br = Element('br')
        br.tail = t
        details.append(br)


def one_course(course: Element, course_data: Element, data_root: Element, root_path: str):
    course.set('id', course_data.get('en_name'))
    title = course.findall('.//*h3')[0]
    title.text = course_data.get('he_name')
    create_topics(course, course_data, data_root, root_path)
    create_details(course, course_data)


def course_str(course: Element):
    indent(course)
    course = tostring(course, encoding='utf8').decode('utf8')
    course = course.replace("<?xml version='1.0' encoding='utf8'?>", '', 1)
    return course


def one_column(col: list[Element], line: str):
    line = line[:len(line) - len('</div>\n')] + '\n'
    for course in col:
        line += course_str(course)
    line += '</div>\n'
    return line


def one_branch(branch_data: Element, path: str, data_root: Element, root_path: str):
    courses = []
    for course_data in branch_data:
        course = deepcopy(COURSE)
        one_course(course, course_data, data_root, root_path)
        courses.append(course)
    mid = len(courses) // 2 + len(courses) % 2
    first_col = courses[:mid]
    second_col = courses[mid:]

    with open(PATH, 'r', encoding='utf8') as temp:
        with open(path + '_', 'wb') as new:
            line = temp.readline()
            while 'id="first_col"' not in line:
                new.write(line.encode('utf8'))
                line = temp.readline()
            line = one_column(first_col, line)
            new.write(line.encode('utf8'))

            while 'id="second_col"' not in line:
                line = temp.readline()
            line = one_column(second_col, line)
            new.write(line.encode('utf8'))

            while 'id="credit"' not in line:
                line = temp.readline()
            new.write(line.encode('utf8'))

            for line in temp:
                new.write(line.encode('utf8'))

    if exists(path):
        remove(path)
    rename(path + '_', path)


def paste_branches(data_root: Element, site_root: str, root_path: str):
    for branch_data in data_root:
        path = join(site_root, branch_data.get('en_name'), 'index.html')
        one_branch(branch_data, path, data_root, root_path)
