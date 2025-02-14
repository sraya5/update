from os import makedirs, stat, chdir
from json import load
from subprocess import run,DEVNULL, CalledProcessError
from copy import deepcopy
from shutil import copy
from datetime import datetime
from update.wp2html import site2html
from xml.etree.ElementTree import XMLParser, parse
from PyLyX import LyX, convert, xhtml_style, correct_name
from helper import *
from sitemap_creator import *
from branches_creator import paste_branches

with open(r'data\math_pages.json', 'r') as f:
    PAGES = load(f)
with open(r'data\replaces.json', 'r') as f:
    REPLACES = load(f)

PARSER = XMLParser(encoding="utf-8")
TOPIC_TEMPLATE = parse(join(REFERENCES, 'xhtml', 'topic.xhtml'), PARSER).getroot()
CSS_FOLDER = 'https://math.srayaa.com/references_files/css'
JS_FILES = ('https://math.srayaa.com/references_files/js/topic.js', )
INPUT_PATH = r'C:\Users\sraya\Documents\HUJI\summaries'
OUTPUT_PATH = r'C:\Users\sraya\Documents\GitHub\math'


def up_output(input_path: str, fmt: str, last_play: datetime, output_path: str):
    if not input_path.endswith('.lyx'):
        return False, False

    last_edit = datetime.fromtimestamp(stat(input_path).st_mtime)

    output_path = splitext(remove_number_sign(output_path))[0]
    makedirs(split(output_path)[0], exist_ok=True)
    file = LyX(input_path)
    if fmt == 'xhtml':
        current, info = convert(file.get_doc(), ('https://math.srayaa.com/references_files/css/topic.css', ), CSS_FOLDER, JS_FILES, True, True)
        template = deepcopy(TOPIC_TEMPLATE)
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
    if output_path:
        print('start convert to xhtml...')
        index_xhtml = dir_play(input_path, up_output, ('xhtml', time), output_path, info_print=False)
        print('end convert to xhtml.')
        index_string = index2string(index_xhtml)
        if index_string:
            print('\n\nThe conversion of the following files to xhtml is failed:')
            print(index_string)
    if pdf_path:
        print('\n******start convert to pdf******')
        index_pdf = dir_play(input_path, up_output, ('pdf4', time), pdf_path)
        print('\n******end convert to pdf******')
        index_string = index2string(index_pdf)
        if index_string:
            print('\n\nThe conversion of the following files to pdf is failed:')
            print(index_string)
    if lyx_path:
        print('\n******start copy LyX******')
        index_lyx = dir_play(input_path, up_output, ('lyx', time), lyx_path)
        print('\n******end copy LyX******')
        index_string = index2string(index_lyx)
        if index_string:
            print('\n\nThe coping of the following files failed:')
            print(index_string)

    with open('data/last_play.txt', 'w') as lp:
        now = datetime.now()
        now = str(now)
        lp.write(now[:19])

    if not test_mode:
        result = ''
        try:
            print('\nupdate site with git.\nthis will take some time, please wait.')
            chdir(output_path)
            result = run(['git', 'add', '.'], check=True, stdout=DEVNULL, stderr=DEVNULL)
            result = run(['git', 'commit', '-m', 'auto commit'], check=True, stdout=DEVNULL, stderr=DEVNULL)
            result = run(['git', 'push'], check=True, stdout=DEVNULL, stderr=DEVNULL)
            print('successful update site with git.')
        except CalledProcessError as e:
            print('an error occurred when update site with git.')
            print(f'error massage: "{e}"')
            print(f'cmd result is {result}')


def main():
    site2html(PAGES, REPLACES, ('https://math.srayaa.com/references_files/css/main.css',),
              wp_root=WP_ROOT, site_root=SITE_ROOT, wp_content=join(REFERENCES, 'wp-content'), wp_includes=join(REFERENCES, 'wp-includes'))
    print('create sitemap...')
    lst = create_list(SITEMAP_XML, '../../', SITEMAP_XML, '../../')
    paste_list(join(SITE_ROOT, 'about', 'sitemap', 'index.html'), lst)
    print('create branches...')
    html2xhtml(join(REFERENCES, 'xhtml', 'branch.html'), join(REFERENCES, 'xhtml', 'branch.xhtml'), True)
    paste_branches(SITEMAP_XML, SITE_ROOT, '../')
    # html2xhtml(join(REFERENCES, 'xhtml', 'topic.html'), join(REFERENCES, 'xhtml', 'topic.xhtml'), True)
    # up_all(INPUT_PATH, OUTPUT_PATH, False)


if __name__ == '__main__':
    main()
