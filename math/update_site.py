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
REPLACES_IMG_PATH = {INPUT_PATH: REAL_SITE}
REPLACES_IMG_PATH.update({f'{i}#': '' for i in range(10)})


def up_output(input_path: str, fmt: str, last_play: datetime, output_path: str):
    if input_path.endswith('png'):
        pass # todo: copy images
    if not input_path.endswith('.lyx'):
        return False, False

    last_edit = datetime.fromtimestamp(stat(input_path).st_mtime)

    output_path = splitext(remove_number_sign(output_path))[0]
    makedirs(split(output_path)[0], exist_ok=True)
    file = LyX(input_path)
    if fmt == 'xhtml':
        current, info = convert(file.get_doc(), ('https://math.srayaa.com/references_files/css/topic.css', ), CSS_FOLDER, JS_FILES,
                                js_in_head=True, keep_data=True, replaces=REPLACES_IMG_PATH)
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
    with open(r'data\last_play.txt', 'r') as last_play:
        time = last_play.readline()
        time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')

    if not test_mode:
        pdf_path = lyx_path = output_path
    if output_path:
        print('convert summaries to xhtml...')
        index_xhtml = dir_play(input_path, up_output, ('xhtml', time), output_path, info_print=False)
        index_string = index2string(index_xhtml)
        if index_string:
            print('\n\nThe conversion of the following files to xhtml is failed:')
            print(index_string)
    if pdf_path:
        print('\n******start convert summaries to pdf******')
        index_pdf = dir_play(input_path, up_output, ('pdf4', time), pdf_path)
        print('\n******end convert summaries to pdf******')
        index_string = index2string(index_pdf)
        if index_string:
            print('\n\nThe conversion of the following files to pdf is failed:')
            print(index_string)
    if lyx_path:
        print('\n******start copy LyX files******')
        index_lyx = dir_play(input_path, up_output, ('lyx', time), lyx_path)
        print('\n******end copy LyX files******')
        index_string = index2string(index_lyx)
        if index_string:
            print('\n\nThe coping of the following files failed:')
            print(index_string)

    with open('data/last_play.txt', 'w') as last_play:
        now = datetime.now()
        now = str(now)
        last_play.write(now[:19])


def git_update(output_path):
    try:
        print('\nupdate site with git.\nthis will take some time, please wait.')
        chdir(output_path)
        run(['git', 'add', '.'], check=True, stdout=DEVNULL, stderr=DEVNULL)
        run(['git', 'commit', '-m', 'auto commit'], check=True, stdout=DEVNULL, stderr=DEVNULL)
        run(['git', 'push'], check=True, stdout=DEVNULL, stderr=DEVNULL)
        print('successful update site with git.')
    except CalledProcessError as e:
        print('an error occurred when update site with git.')
        print(f'error massage: "{e}"')


def main(pages=True, sitemap=True, branches=True, summaries=True, test_mode=False):
    if pages:
        site2html(PAGES, REPLACES, ('https://math.srayaa.com/references_files/css/main.css',),
                  wp_root=WP_ROOT, site_root=SITE_ROOT, wp_content=join(REFERENCES, 'wp-content'), wp_includes=join(REFERENCES, 'wp-includes'))
        html2xhtml(join(REFERENCES, 'xhtml', 'branch.html'), join(REFERENCES, 'xhtml', 'branch.xhtml'), True)
        html2xhtml(join(REFERENCES, 'xhtml', 'topic.html'), join(REFERENCES, 'xhtml', 'topic.xhtml'), True)
    if sitemap:
        print('create sitemap...')
        lst = create_list(SITEMAP_XML, '../../', SITEMAP_XML, '../../')
        paste_list(join(SITE_ROOT, 'about', 'sitemap', 'index.html'), lst)
    if branches:
        print('create branches...')
        paste_branches(SITEMAP_XML, SITE_ROOT, '../')
    if summaries:
        up_all(INPUT_PATH, OUTPUT_PATH, test_mode)
    if not test_mode:
        git_update(OUTPUT_PATH)


if __name__ == '__main__':
    main(test_mode=True)
