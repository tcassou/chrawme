# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
import cStringIO
import os

from concurrent.futures import ThreadPoolExecutor

N_EXECUTORS = 2
MAX_CACHE = 25
DEFAULT_FORMAT = 'jpeg'
DEFAULT_THUMBNAIL = os.path.dirname(os.path.realpath(__file__)) + '/thumb.jpg'
THUMB_SIZE = (256, 256)


class BaseImage:
    """
    Generic class representing images and their useful metadata.
    This class is also used as an asynchronous image processing pool to decode / encode / cache images outside the
    main thread.
    """
    _executor = ThreadPoolExecutor(N_EXECUTORS)  # Image processing thread, shared by all instances
    _cache = []                                  # Cache of processed images, shared by all instances

    def __init__(self, image_id, path, name, file_stream, api_metadata, process=False):
        """Generic instantiation of images.

        :param int image_id: id given to the image, defining relative position in directory (sorted by name)
        :param str path: full path of the image directory
        :param str name: image file name
        :param method file_stream: method defining how to stream the file content
        :param class api_metadata: API metadata wrapper
        :param bool process: True to decode and encore image file at instantiation, False to wait

        :return: None
        :rtype: NoneType
        """
        self.id = image_id                              # Index of image in the folder (sorted by name)
        self.path = path                                # Directory contanining the image
        self.name = name                                # Name of the iamge file
        self.file_stream = file_stream                  # By efault, returning the file name in local dir
        self.api_metadata = api_metadata                # Wrapper of API meta data
        self.short_name = self.shorten_name()           # Short name
        self.ext = os.path.splitext(name)[1].lower()    # Extension of image file
        self.decoded = None                             # PIL Image
        self.encoded = None                             # base64 encoded version of the image
        self.size = (None, None)                        # Width / Height of the image
        self.orientation = None                         # Orientation: 0 = landspace / 1 = portrait
        self.thumbnail = self.read_thumbnail()          # base64 encoded thumbbail
        if process:
            self.decode_encode()

    def shorten_name(self):
        """Make a shorter version of image name, for display purposes.

        :return: short name
        :rtype: str
        """
        return self.name[:15] + ('..' if len(self.name) > 15 else '')

    def thumbnail_name(self):
        """Build thumbnail file name from image name.

        If local file, the thumbnail will be stored along the file itself.
        If remote, the thumbnail is stored in the .cache directory.

        :return: file name
        :rtype: str
        """
        if self.api_metadata.remote:
            path = (
                os.path.dirname(__file__) + '/.cache/' +
                self.api_metadata.name + '_' + self.path.replace('/', '_') + '_'
            )
            name = self.name[:-len(self.ext)].replace('/', '_')
        else:
            path = self.path + '/'
            name = '.' + self.name[:-len(self.ext)]

        return path + name + '_thumb.jpg'

    def has_thumbnail(self):
        """Check if image thumbnail already exists on disk.

        :return: True if exists
        :rtype: bool
        """
        return os.path.isfile(self.thumbnail_name())

    def read_thumbnail(self):
        """Create a PIL image from a thumbnail file.

        :return: thumbnail
        :rtype: base64 string
        """
        thumb_file = self.thumbnail_name() if self.has_thumbnail() else DEFAULT_THUMBNAIL
        with open(thumb_file, "rb") as image_file:
            thumb_bytes = image_file.read()
        return base64.b64encode(thumb_bytes)

    def save_thumbnail(self):
        """Save thumbnail image to disk.

        :return: None
        :rtype: NoneType
        """
        if os.path.isfile(self.thumbnail_name()):
            return
        thumb = self.decode() if self.decoded is None else self.decoded.copy()
        thumb.thumbnail(THUMB_SIZE)
        thumb.save(self.thumbnail_name())
        self.thumbnail = self.read_thumbnail()

    def decode_encode(self):
        """Decode image file on disk (depend on file format), and encode it to base64 to be displayed in browser.

        :return: None
        :rtype: NoneType
        """
        # For now, being in the cache <=> being decoded and encoded
        if self in self._cache:
            return
        self.flush_cache()
        self.decoded = self.decode()
        self.encoded = self.b64encode()
        # Decoding / encoding is costly, so while we're at it we can save a thumbnail file (much faster)
        self.save_thumbnail()
        self._cache.append(self)

    def decode_encode_async(self):
        """Asynchronously decode and encore image, sending it as the job to the class executor(s).

        :return: None
        :rtype: NoneType
        """
        self._executor.submit(self.decode_encode)

    def decode(self):
        """Decode image from file - defined in children classes as the process depend on the image initial format.

        :return: decoded image
        :rtype: PIL Image
        """
        raise NotImplementedError

    def b64encode(self):
        """Encode image to base64.

        :return: base64 encoded image
        :rtype: base64 string
        """
        # For now, first encoding into a simple, intermediate format to then encode to b64 - very slow
        tmp_buffer = cStringIO.StringIO()
        self.decoded.save(tmp_buffer, format=DEFAULT_FORMAT)
        # Encoding in base64, fairly fast
        return base64.b64encode(tmp_buffer.getvalue())

    def flush_cache(self):
        """Flush cache of encoded images to avoid having too many encoded (i.e. heavy) image objects in RAM.

        :return: None
        :rtype: NoneType
        """
        if len(self._cache) > MAX_CACHE:
            gaps = [img.id - self.id for img in self._cache]
            agg = min if min(gaps) <= -2 else max
            oldest_id = agg(enumerate(gaps), key=lambda x: x[1])[0]
            oldest = self._cache.pop(oldest_id)
            oldest.encoded = None
            oldest.decoded = None

    def clear_queue(self):
        """Clear ThreadPool queue.

        :return: None
        :rtype: NoneType
        """
        self._executor._work_queue.queue.clear()
