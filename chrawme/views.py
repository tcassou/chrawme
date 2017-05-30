# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponsePermanentRedirect


def redirect(request, redirect_to):
    return HttpResponsePermanentRedirect(redirect_to)
