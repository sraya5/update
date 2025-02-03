from os.path import isfile, isdir, splitext, split, join, exists
from os import scandir, makedirs, stat
from copy import deepcopy
from shutil import copy
from datetime import datetime
from lxml.etree import XMLParser, parse, fromstring
from PyLyX import LyX, convert, xhtml_style, correct_name
from helper import *

PARSER = XMLParser(recover=True, encoding="utf-8")
TOPIC_TEMPLATE_TREE = parse(r'C:\Users\sraya\Documents\GitHub\math\references_files\xhtml\topic.xhtml', PARSER)
CSS_FILES = ('https://math.srayaa.com/references_files/css/topic.css', )
JS_FILES = ('https://math.srayaa.com/references_files/js/topic.js', )


def dir_play(input_path: str, func, args=(), output_path='', index=None, skip=None):
    if skip and input_path in skip:
        return None
    elif index is None:
        index = {}

    if exists(input_path):
        if isfile(input_path) and input_path.endswith('.lyx'):
            name = split(input_path)[1]
            file = LyX(input_path)
            result, error = func(file, output_path, *args)
            if result:
                print(f'\t\t   {name}')
                index[name] = True
            elif error:
                index[name] = False
        elif isdir(input_path):
            print(f'\ndirectory: {input_path}')
            index[input_path] = {}
            for entry in scandir(input_path):
                dir_play(join(input_path, entry.name), func, args, join(output_path, entry.name), index[input_path], skip)
    else:
        raise FileNotFoundError(f'not found such file or directory: {input_path}')
    return index


def up_output(file: LyX, output_path: str, fmt: str, last_play: datetime):
    input_path = file.get_path()
    last_edit = datetime.fromtimestamp(stat(input_path).st_mtime)

    output_path = splitext(remove_number_sign(output_path))[0]
    makedirs(split(output_path)[0], exist_ok=True)
    if fmt == 'xhtml':
        root, info = convert(file.get_doc(), CSS_FILES, JS_FILES)
        current = fromstring(xhtml_style(root, output_path, False, info).encode('utf8'))
        template = deepcopy(TOPIC_TEMPLATE_TREE)
        output_path = correct_name(output_path, '.xhtml')
        merge_xhtml(template, current, output_path)
        # with open(output_path, 'wb') as f:
        #     f.write(xhtml_bytes)
        return True, False
    elif last_edit > last_play:
        if fmt == 'lyx':
            output_path = correct_name(output_path, '.lyx')
            copy(input_path, output_path)
            result = True
        else:
            output_path = correct_name(output_path, '.pdf')
            result = file.export(fmt, output_path)
        return result, not result
    else:
        return False, False


def up_all(input_path: str, xhtml_path='', pdf_path='', lyx_path=''):
    # with open(r'data\last_play.txt', 'r') as lp:
    #     time = lp.readline()
    #     time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    time = datetime.strptime('2000-10-31 13:46:34', '%Y-%m-%d %H:%M:%S')

    index_xhtml, index_pdf = {}, {}
    if xhtml_path:
        print('\n******start convert to xhtml******')
        dir_play(input_path, up_output, ('xhtml', time), xhtml_path, index_xhtml)
        print('\n******end convert to xhtml******')
        index_string = index2string(index_xhtml)
        if index_string:
            print('\n\nThe convert to xhtml of the following file failed:')
            print(index_string)
    if pdf_path:
        print('\n******start convert to pdf******')
        dir_play(input_path, up_output, ('pdf4', time), pdf_path, index_pdf)
        print('\n******end convert to pdf******')
        index_string = index2string(index_pdf)
        if index_string:
            print('\n\nThe convert to pdf of the following file failed:')
            print(index_string)
    if lyx_path:
        print('\n******start copy LyX******')
        dir_play(input_path, up_output, ('lyx', time), pdf_path, index_pdf)
        print('\n******end copy LyX******')

    with open('data/last_play.txt', 'w') as lp:
        now = datetime.now()
        now = str(now)
        lp.write(now[:19])

if __name__ == '__main__':
    INPUT_PATH = r'C:\Users\sraya\Documents\HUJI\summaries'
    XHTML_PATH = r'C:\Users\sraya\Documents\GitHub\math'
    # PDF_PATH = r'C:\Users\sraya\Documents\GitHub\math'
    PDF_PATH = ''
    LYX_PATH = ''
    MACROS_OLD = 'C:\\Users\\sraya\\AppData\\Roaming\\LyX2.4\\macros\\MacrosStandard.lyx'
    MACROS_NEW = 'C:\\Users\\sraya\\AppData\\Roaming\\LyX2.4\\macros\\MKmacros.lyx'
    up_all(INPUT_PATH, XHTML_PATH, PDF_PATH, LYX_PATH)
