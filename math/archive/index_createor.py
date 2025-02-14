from os import remove
from os.path import isfile, isdir, split, exists, join, splitext
from xml.etree.ElementTree import Element, indent, tostring
from PyLyX import LyX
from PyLyX.package_helper import correct_brackets
from helper import dir_play, remove_number_sign

LYX_FILES_OLD = r'C:\Users\sraya\Documents\HUJI\archive\for_LyX\summaries'

def create_dict(input_path: str):
    if input_path.endswith('.lyx'):
        return True, False
    else:
        return False, False

def one_file(topic, topic_el: Element):
    file = LyX(topic)

    course = file.find('80')
    if course is not None:
        try:
            number = int(course.text)
            topic_el.set('course_number', str(number))
        except ValueError:
            pass

    lecturer = file.find('מרצה')
    if lecturer is not None:
        lecturer = lecturer.text.split(':')
        lecturer = correct_brackets(lecturer[-1].strip())[0]
        if 0 < len(lecturer) < 20:
            topic_el.set('lecturer', lecturer)

    tutor = file.find('מתרגל')
    if tutor is not None:
        tutor = tutor.text.split(':')
        tutor = correct_brackets(tutor[-1].strip())[0]
        if 0 < len(tutor) < 20:
            topic_el.set('tutor', tutor)

    semester = file.find('סמסטר')
    if semester is not None:
        semester = semester.text
        semester = semester.replace('סמסטר ', '')
        semester = semester.replace(", האונ' העברית", '')
        semester = semester.replace(", האוניברסיטה העברית", '')
        if 0 < len(semester) < 20:
            topic_el.set('semester', semester)


def extract_name(path: str):
    name = split(path)[1]
    name = splitext(name)[0]
    name = remove_number_sign(name)
    return name



def old_main(path: str):
    dictionary = dir_play(path, create_dict, info_print=False)
    dict_root = dictionary[path]
    index_root = Element('root')
    for branch in dict_root:
        branch_el = Element('branch', attrib={'en_name': extract_name(branch)})
        index_root.append(branch_el)
        for course in dict_root[branch]:
            course_el = Element('course', attrib={'en_name': extract_name(course)})
            branch_el.append(course_el)
            for topic in dict_root[branch][course]:
                topic_el = Element('topic', attrib={'en_name': extract_name(topic)})
                if isfile(join(course, topic)):
                    one_file(join(course, topic), topic_el)
                elif isdir(topic) and not topic.endswith('figures'):
                    attrib = None
                    for file in dict_root[branch][course][topic]:
                        if isfile(join(topic, file)):
                            file_el = Element('file', attrib={'en_name': extract_name(file)})
                            one_file(join(topic, file), file_el)
                            name = file_el.attrib.pop('en_name')
                            if attrib is None:
                                attrib = file_el.attrib
                            elif attrib != file_el.attrib:
                                print(name)
                                print(attrib)
                                print(file_el.attrib)
                                print()
                                attrib = None
                        elif isdir(file) and not file.endswith('figures'):
                            for subtopic in dict_root[branch][course][topic][file]:
                                if isfile(join(file, subtopic)):
                                    subtopic_el = Element('subtopic', attrib={'en_name': extract_name(subtopic)})
                                    one_file(join(file, subtopic), subtopic_el)
                                    name = subtopic_el.attrib.pop('en_name')
                                    subtopic_el.clear()
                                    subtopic_el.set('en_name', name)
                                    topic_el.append(subtopic_el)
                    if attrib is not None:
                        course_el.attrib.update(attrib)
                else:
                    continue
                course_el.append(topic_el)

    indent(index_root)
    bytes_index = tostring(index_root, 'utf8')
    path = r'C:\Users\sraya\Downloads\index.xml'
    if exists(path):
        remove(path)
    with open(path, 'wb') as file:
        file.write(bytes_index)

if __name__ == '__main__':
    old_main(LYX_FILES_OLD)
