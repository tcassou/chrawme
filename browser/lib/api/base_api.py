# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from browser.lib.image.simple_image import SimpleImage
from browser.lib.image.raw_image import RawImage


class BaseAPI:

    # Caching data and sharing between views. Not really scalable to multiple processes, but good enough for local use.
    path = None                   # Current directory
    folders = None                # List of folders in directory
    images = None                 # List of images in directory
    autocomplete_source = None    # Tree structure for search bar

    @classmethod
    def folder_content(cls, path):
        """Describe the contents of a folder.

        :param str path: path to folder

        :return: list of directories and images in the folder, and flattened directory tree structure for search
        :rtype: [{str: object}], [browser.lib.image.base_image.BaseImage], [str]
        """
        if cls.path != path:
            content = cls.list_content(path)
            cls.path = path
            cls.list_folders(path, content)
            cls.list_images(path, content)
            cls.list_autocomplete_source(path, content)

        return cls.folders, cls.images, cls.autocomplete_source

    @classmethod
    def create_image(cls, image_id, path, name, process=False):
        """Create an image object depending on the file format.

        :param int image_id: id of the image in folder
        :param str path: root directory
        :param str name: image file name
        :param bool process: flag to process (i.e. decode) the image

        :return: image object
        :rtype: browser.lib.image.base_image.BaseImage
        """
        image_class = RawImage if RawImage.is_raw(name) else SimpleImage
        return image_class(image_id, path, name, cls.file_stream(), api_metadata=cls.Meta, process=process)
