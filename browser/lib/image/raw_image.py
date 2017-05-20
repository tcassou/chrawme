# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import numpy as np

from browser.lib.image.base_image import BaseImage
from PIL import Image
from rawkit.raw import Raw

RAW_FORMATS = ['.cr2']


class RawImage(BaseImage):

    def decode(self):
        """Decode raw image from file using rawkit.raw.
        Size of image from metadata - depends on image orientation, refer to below link for more info.
            http://www.impulseadventure.com/photo/exif-orientation.html

        :return: decoded image
        :rtype: PIL Image
        """
        raw = Raw(self.file_stream(self.path + '/' + self.name))
        if raw.metadata.orientation >= 5:
            self.size = raw.metadata.height, raw.metadata.width
            self.orientation = 1
        else:
            self.size = raw.metadata.width, raw.metadata.height
            self.orientation = 0
        # Raw to bytes - maybe at some point we'll want to keep the Raw object too?
        image_bytes = np.array(raw.to_buffer())
        return Image.frombytes('RGB', self.size, image_bytes)

    @staticmethod
    def is_raw(name):
        """Static method to check if an image has a raw format.

        :param str name: file name

        :return: True if raw, False otherwise
        :rtype: bool
        """
        return os.path.splitext(name)[1].lower() in RAW_FORMATS
