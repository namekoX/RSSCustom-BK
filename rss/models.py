from django.db import models
from django.utils import timezone

class Entry(models.Model):
    no = models.AutoField('名前',max_length=255,primary_key=True)
    url = models.CharField('URL',max_length=255)
    user_id = models.CharField('ユーザーID',max_length=255, null=True, blank=True)
    site_name = models.CharField('サイト名',max_length=255)
    inclede_category = models.CharField('カテゴリ含む',max_length=255, null=True, blank=True)
    inclede_subject = models.CharField('件名含む',max_length=255, null=True, blank=True)
    inclede_creater = models.CharField('投稿者含む',max_length=255, null=True, blank=True)
    max_count = models.IntegerField('最大件数', null=True, blank=True)
    limit_day = models.IntegerField('日付以内', null=True, blank=True)
    version = models.CharField('バージョン',max_length=10)
    create_at = models.DateField('作成日',default=timezone.now, blank=True)
    update_at = models.DateField('更新日',default=timezone.now, blank=True)
    def __str__(self):
        return '<id:' + str(self.no) + ',' + self.site_name + '>'

class LoginUser(models.Model):
    user_id = models.CharField('ユーザーID',max_length=255,primary_key=True)
    site_id = models.CharField('サイトID',max_length=2,default='1', blank=True)
    password = models.CharField('パスワード',max_length=255)
    create_at = models.DateField('作成日',default=timezone.now, blank=True)
    update_at = models.DateField('更新日',default=timezone.now, blank=True)
    def __str__(self):
        return '<id:' + self.user_id + ',' + self.site_id + '>'