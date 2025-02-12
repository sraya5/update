from os import makedirs, stat, chdir
from json import load
from subprocess import run,DEVNULL
from copy import deepcopy
from shutil import copy
from datetime import datetime
from update.wp2html import site2html
from xml.etree.ElementTree import XMLParser, parse
from PyLyX import LyX, convert, xhtml_style, correct_name
from helper import *

with open(r'data\math_pages.json', 'r') as f:
    PAGES = load(f)
with open(r'data\replaces.json', 'r') as f:
    REPLACES = load(f)
SITE_ROOT = r'C:\Users\sraya\Documents\GitHub\math'
WP_ROOT = r'C:\Users\sraya\Documents\LocalWP\math\app\public'
REFERENCES = join(SITE_ROOT, r'references_files')

PARSER = XMLParser(encoding="utf-8")
TOPIC_TEMPLATE_TREE = parse(r'C:\Users\sraya\Documents\GitHub\math\references_files\xhtml\topic.xhtml', PARSER).getroot()
CSS_FOLDER = 'https://math.srayaa.com/references_files/css'
JS_FILES = ('https://math.srayaa.com/references_files/js/topic.js', )
INPUT_PATH = r'C:\Users\sraya\Documents\HUJI\summaries'
OUTPUT_PATH = r'C:\Users\sraya\Documents\GitHub\math'


def up_output(input_path: str, output_path: str, fmt: str, last_play: datetime):
    if not input_path.endswith('.lyx'):
        return False, False

    last_edit = datetime.fromtimestamp(stat(input_path).st_mtime)

    output_path = splitext(remove_number_sign(output_path))[0]
    makedirs(split(output_path)[0], exist_ok=True)
    file = LyX(input_path)
    if fmt == 'xhtml':
        current, info = convert(file.get_doc(), ('https://math.srayaa.com/references_files/css/topic.css', ), CSS_FOLDER, JS_FILES, True, True)
        template = deepcopy(TOPIC_TEMPLATE_TREE)
        xhtml_style(current, output_path, False, info)
        output_path = correct_name(output_path, '.xhtml')
        merge_xhtml(template, current, output_path, info['toc'])
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


def up_all(input_path: str, output_path: str, test_mode=False, pdf_path='', lyx_path=''):
    # with open(r'data\last_play.txt', 'r') as lp:
    #     time = lp.readline()
    #     time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    time = datetime.strptime('2000-10-31 13:46:34', '%Y-%m-%d %H:%M:%S')

    # if not test_mode:
    #     pdf_path = lyx_path = output_path
    index_xhtml, index_pdf, index_lyx = {}, {}, {}
    if output_path:
        print('\n******start convert to xhtml******')
        dir_play(input_path, up_output, (output_path, 'xhtml', time), index_xhtml)
        print('\n******end convert to xhtml******')
        index_string = index2string(index_xhtml)
        if index_string:
            print('\n\nThe convert to xhtml of the following file failed:')
            print(index_string)
    if pdf_path:
        print('\n******start convert to pdf******')
        dir_play(input_path, up_output, ('pdf4', time), pdf_path)
        print('\n******end convert to pdf******')
        index_string = index2string(index_pdf)
        if index_string:
            print('\n\nThe convert to pdf of the following file failed:')
            print(index_string)
    if lyx_path:
        print('\n******start copy LyX******')
        dir_play(input_path, up_output, ('lyx', time), pdf_path)
        print('\n******end copy LyX******')

    with open('data/last_play.txt', 'w') as lp:
        now = datetime.now()
        now = str(now)
        lp.write(now[:19])

    if not test_mode:
        print('\nupdate site with git.\nthis will take some time, please wait.')
        chdir(output_path)
        run(['git', 'add', '.'], check=True, stdout=DEVNULL, stderr=DEVNULL)
        run(['git', 'commit', '-m', 'auto commit'], check=True, stdout=DEVNULL, stderr=DEVNULL)
        run(['git', 'push'], check=True, stdout=DEVNULL, stderr=DEVNULL)
        print('successful update site with git.')


def main():
    site2html(PAGES, REPLACES, ('https://math.srayaa.com/references_files/css/main.css',),
              wp_root=WP_ROOT, site_root=SITE_ROOT, wp_content=join(REFERENCES, 'wp-content'), wp_includes=join(REFERENCES, 'wp-includes'))
    html2xhtml(join(REFERENCES, r'xhtml\topic.html'), join(REFERENCES, r'xhtml\topic.xhtml'), True)
    html2xhtml(join(REFERENCES, r'xhtml\branch.html'), join(REFERENCES, r'xhtml\branch.xhtml'), True)
    up_all(INPUT_PATH, OUTPUT_PATH, False)

if __name__ == '__main__':
    main()
