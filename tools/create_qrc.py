#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import subprocess

template_header = '<!DOCTYPE RCC>\n<RCC version="1.0">\n\t<qresource prefix="/">\n'
template_footer = '\n\t</qresource>\n</RCC>\n'


def create_qrc():
    with open(qrc_file, 'w') as f:
        for root, dirs, files in os.walk(images_dir, topdown=False):
            template = [f'\t\t<file alias="{name}">{os.path.join("..", "sources", "images", name)}</file>' for name in files if
                        name[-4:] in ['.png', '.ico', '.svg']]
            f.write(template_header + '\n'.join(template) + template_footer)


def create_py():
    process = subprocess.Popen(['pyrcc5.exe', qrc_file, '-o', py_file], stdout=subprocess.PIPE, shell=True)
    while True:
        line = process.stdout.readlines()
        if not line:
            process.kill()
            break
        else:
            print(line)


if __name__ == '__main__':
    this_dir = os.path.dirname(os.path.realpath(__file__))
    sources_dir = os.path.abspath(os.path.join('..', 'sources'))
    images_dir = os.path.join(sources_dir, 'images')
    qrc_file = os.path.join(sources_dir, 'sources.qrc')
    py_file = os.path.join(sources_dir, 'sources.py')

    create_qrc()
    create_py()
