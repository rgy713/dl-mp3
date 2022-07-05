# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import User
from .models import DownloadInfo
from django.contrib.auth.models import Group

class DownloadInfoAdmin(admin.ModelAdmin):
    list_display = ('username', 'url','title', 'file_name', 'date')
    search_fields = ('username', 'url','title', 'filename', 'date')


    def get_actions(self, request):
        actions = super(DownloadInfoAdmin, self).get_actions(request)
        if request.user.username[0].upper() != 'J':
            del actions['delete_selected']
        return actions

# Register your models here.
# admin.site.unregister(Group)
admin.site.register(DownloadInfo, DownloadInfoAdmin)
