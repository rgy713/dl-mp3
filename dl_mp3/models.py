# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class DownloadInfo(models.Model):
    username = models.CharField(max_length=15)
    url = models.CharField(max_length=256)
    title = models.CharField(max_length=256)
    file_name = models.CharField(max_length=256)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "ダウンロード情報"
        verbose_name_plural = "ダウンロード情報"

class AccessInfo(models.Model):
    login = models.IntegerField(default=0)
    regist = models.IntegerField(default=0)