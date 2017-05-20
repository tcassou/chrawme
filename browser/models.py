# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from os.path import expanduser


# Browser settings
class Setting(models.Model):
    # Fields
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=500)

    # Class methods
    @classmethod
    def defaults(cls):
        return {
            'home_path': expanduser("~"),
        }

    @classmethod
    def by_name(cls, name):
        try:
            return cls.objects.get(name=name)
        except ObjectDoesNotExist:
            return cls.defaults()[name]

    @classmethod
    def all(cls):
        stored = cls.objects.all()
        default = cls.defaults()
        return { key: stored.filter(name=key).first() or val for key, val in default.iteritems() }
