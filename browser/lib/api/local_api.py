# -*- coding: utf-8 -*-

import os
from datetime import datetime

from browser.lib.api.base_api import BaseAPI

from browser.lib.image.simple_image import SimpleImage
from browser.lib.image.simple_image import SIMPLE_FORMATS
from browser.lib.image.raw_image import RawImage
from browser.lib.image.raw_image import RAW_FORMATS

TREE_MAX_DEPTH = 4


class LocalAPI(BaseAPI):

    class Meta:
        name = 'local'
        remote = False

    @classmethod
    def list_content(cls, path):
        """List directory contents needed to enumerate files and folders.

        :param str path: path to directory

        :return: folder content
        :rtype: [object]
        """
        return sorted(os.listdir(path))

    @classmethod
    def list_folders(cls, path, content):
        """List folders under path.

        :param str path: current path
        :param [object] content: current folder contents

        :return: None
        :rtype: NoneType
        """
        cls.folders = [
            {
                'label': f,
                'value': os.path.join(path, f),
                'last_modified': datetime.fromtimestamp(os.path.getmtime(os.path.join(path, f))).strftime('%Y-%m-%d'),
            }
            for f in content if os.path.isdir(os.path.join(path, f)) and cls.should_display_folder(path, f)
        ]

    @classmethod
    def list_images(cls, path, content):
        """List images under path.

        :param str path: current path
        :param [object] content: current folder contents

        :return: None
        :rtype: NoneType
        """
        cls.images = [
            cls.create_image(i, path, name, process=False)
            for i, name in enumerate([f for f in content if cls.should_display_image(f)])
        ]

    @classmethod
    def list_autocomplete_source(cls, path, content):
        """Find the directory tree structure excluding files, to use in the autocomplete feature.

        :param str path: directory to scan
        :param [object] content: current folder contents

        :return: list of directories
        :rtype: [str]
        """
        cls.autocomplete_source = cls.flatten_directory_tree(path)

    @classmethod
    def flatten_directory_tree(cls, path, max_depth=TREE_MAX_DEPTH):
        """Recursively find the directory tree structure excluding files, to use in the autocomplete feature.

        :param str path: directory to scan
        :param int max_depth: recursion limit

        :return: list of directories
        :rtype: [str]
        """
        if max_depth == 0:
            return []

        content = os.listdir(path)
        folders = [
            os.path.join(path, f) for f in content
            if os.path.isdir(os.path.join(path, f)) and cls.should_display_folder(path, f)
        ]
        return sum([cls.flatten_directory_tree(f, max_depth=max_depth - 1) for f in folders], folders)

    @classmethod
    def should_display_image(cls, name):
        """Decide if an image file should be displayed in the browser.

        Only specific formats are displayed, if the image name does not start with '.'.

        :param str name: file name

        :return: True if image should be displayed
        :rtype: bool
        """
        if name.startswith('.'):
            return False
        return os.path.splitext(name)[1].lower() in SIMPLE_FORMATS + RAW_FORMATS

    @classmethod
    def should_display_folder(cls, path, name):
        """Decide if a folder should be displayed in the browser.

        Only folders with read access righrs are displayed, if their name does not start with '.'.

        :param str path: root of the folder
        :param str name: folder name

        :return: True if folder should be displayed
        :rtype: bool
        """
        try:
            # a = os.access(os.path.join(path, name), os.R_OK)
            b = '.' not in name
        except UnicodeDecodeError:
            print ''
            print path
            print name
            print ''
        return '.' not in name and os.access(os.path.join(path, name), os.R_OK)

    @classmethod
    def file_stream(cls):
        """Define the file input stream to read the image from local machine.

        :return: method to read the file
        :rtype: method
        """
        def read_file(filename):
            """Read the image file from local tree.

            :param str filename: name of the image

            :return: file name
            :rtype: str
            """
            return filename

        return read_file
