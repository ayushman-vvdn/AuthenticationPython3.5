# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


class Captcha(models.Model):
    captcha = models.CharField(max_length=6)
    expire = models.CharField(max_length=20)
    created_timestamp = models.DateTimeField(default=datetime.now)

