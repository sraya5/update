from os import remove, chmod, makedirs, chdir
from os.path import exists, join, split, isdir
from shutil import rmtree, copy
from stat import S_IWRITE
from requests import get
from requests.exceptions import ConnectionError
from subprocess import run, DEVNULL, CalledProcessError
from xml.etree.ElementTree import Element, tostring
from update.auto_folder import dir_play


def create_css(path: str):
    attrib = {'rel': 'stylesheet', 'type': 'text/css', 'href': path}
    return Element('link', attrib=attrib)


def create_script(source: str, async_=''):
    attrib = {'src': source}
    if async_:
        attrib['async'] = async_
    return Element('script', attrib=attrib)


def css_and_js(html_code, css_files=(), js_files=()):
    css_code = ''
    for path in css_files:
        css_code += tostring(create_css(path), encoding='unicode') + '\n'
    js_code = ''
    for path in js_files:
        js_code += tostring(create_script(path), encoding='unicode') + '\n'
    html_code = html_code.replace('</head>', css_code + js_code + '</head>')
    return html_code


def site2html(pages: dict[str, str], replaces: dict[str, str], css_files=(), js_files=(),
              wp_root='', site_root='', wp_content='', wp_includes=''):
    for url in pages:
        try:
            src = get(url)
        except ConnectionError:
            print(f'invalid url: {url}')
            continue
        if src.status_code not in {200, 404} or (src.status_code == 404 and not url.endswith('404')):
            print(f'invalid url: {url}')
            continue
        src_txt = src.text
        dst = pages[url]
        if exists(dst):
            remove(dst)
        for old in replaces:
            src_txt = src_txt.replace(old, replaces[old])
        src_txt = css_and_js(src_txt, css_files, js_files)
        makedirs(split(dst)[0], exist_ok=True)
        with open(dst, 'w', encoding='utf8') as file:
            file.write(src_txt)
        print(f'successful conversion: {url}')
    if wp_root and site_root:
        wp_content = wp_content if wp_content else join(site_root, 'wp-content')
        if exists(wp_content):
            if isdir(wp_content):
                rmtree(wp_content, onerror=remove_readonly)
            else:
                remove_readonly(remove, wp_content, None)
        print('\ncopy the "wp-content" folder.\nthis will take some time, please wait.')
        copy_wp(join(wp_root, 'wp-content'), wp_content)

        wp_includes = wp_includes if wp_includes else join(site_root, 'wp-includes')
        if exists(wp_includes):
            if isdir(wp_content):
                rmtree(wp_includes, onerror=remove_readonly)
            else:
                remove_readonly(remove, wp_includes, None)
        print('copy the "wp-includes" folder.\nthis will take some time, please wait.')
        copy_wp(join(wp_root, 'wp-includes'), wp_includes)

        print('successful copy of "wp-content" and "wp-includes".\n')


def remove_readonly(func, path, _):
    """Change file permissions and retry deleting"""
    chmod(path, S_IWRITE)  # Make it writable
    func(path)


def one_file(src: str, dst: str):
    if src.endswith('.php'):
        return False, False
    else:
        makedirs(split(dst)[0], exist_ok=True)
        try:
            copy(src, dst)
        except PermissionError:
            print(f'can not copy {src}')
        return True, False


def copy_wp(src, dst):
    dir_play(src, one_file, output_path=dst, info_print=False)


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
