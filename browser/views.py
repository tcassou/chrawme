# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse

import json

from browser.lib.api.local_api import LocalAPI
from browser.lib.api.hubic_api import HubicAPI
from browser.lib.image.base_image import MAX_CACHE

from browser.models import Setting

# '/media/thomas/external/Pictures'
GALLERY_NCOL = 6


def index(request):
    return render_content(request, LocalAPI, Setting.by_name('home_path'))


def local(request, path=Setting.by_name('home_path')):
    return render_content(request, LocalAPI, path)


def hubic(request, path=''):
    return render_content(request, HubicAPI, path)


def local_show(request, path, image_id):
    return show(request, LocalAPI, path, image_id)


def hubic_show(request, path, image_id):
    return show(request, HubicAPI, path, image_id)


def show(request, api, path, image_id):
    # Practically path has not changed and we could directly use current_content, this is just safer
    _, images, _ = api.folder_content(path)
    # Fetching requested image and clearing background queue, since we're going to replenish it with prioritary jobs
    image = images[int(image_id)]
    image.clear_queue()
    # Asynchronously processing MAX_CACHE images (previous and few next ones)
    for offset in range(1, MAX_CACHE) + [-1]:
        images[(int(image_id) + offset) % len(images)].decode_encode_async()

    # Processing current image (will skip automatically if previously processed)
    image.decode_encode()
    context = {
        'api': api.Meta.name,
        'image': image,
        'prev_id': (int(image_id) - 1) % len(images),
        'next_id': (int(image_id) + 1) % len(images),
        'n_images': len(images),
    }
    return render(request, 'browser/show.html', context)


def render_content(request, api, path, ncol=GALLERY_NCOL):
    folders, images, autocomplete_source = api.folder_content(path)
    images =  [images[x:min(x + ncol, len(images))] for x in range(0, len(images), ncol)]
    context = {
        'api': api.Meta.name,
        'path': path,
        'folders': folders,
        'autocomplete_source': json.dumps(autocomplete_source),
        'images': {
            'array': images,
            'ncols': ncol,
        }
    }
    return render(request, 'browser/index.html', context)
