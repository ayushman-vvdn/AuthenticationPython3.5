# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User

User._meta.get_field('first_name').max_length = 100
User._meta.get_field('last_name').max_length = 100
User._meta.get_field('username').max_length = 200
User._meta.get_field('password').max_length = 400


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    nick_name = models.CharField(max_length=50, null=True, blank=True)
    level = models.FloatField(default=0.0, null=False, blank=False)
    unique_id = models.CharField(max_length=20, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=4, null=True, blank=True)

    # we won't delete any user. it get archived
    is_archived = models.BooleanField(default=False)

    created_timestamp = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    updated_timestamp = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.user.email

    class Meta:
        app_label = 'accounts'


