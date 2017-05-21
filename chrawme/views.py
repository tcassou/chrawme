# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponsePermanentRedirect


def redirect(request, path):
    return HttpResponsePermanentRedirect(path)
