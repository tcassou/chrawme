# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from browser.lib.image.base_image import BaseImage
from PIL import Image

SIMPLE_FORMATS = ['.png', '.jpg']


class SimpleImage(BaseImage):

    def decode(self):
        """Decode raw image from file using PIL.

        :return: decoded image
        :rtype: PIL Image
        """
        decoded = Image.open(self.file_stream(self.path + '/' + self.name))
        self.size = decoded.size
        self.orientation = 0 if self.size[0] > self.size[1] else 1
        return decoded
