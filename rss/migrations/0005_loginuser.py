# Generated by Django 2.2.6 on 2019-11-07 13:03

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('rss', '0004_entry_inclede_creater'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoginUser',
            fields=[
                ('user_id', models.CharField(max_length=255, primary_key=True, serialize=False, verbose_name='ユーザーID')),
                ('site_id', models.CharField(default='1', max_length=2, verbose_name='サイトID')),
                ('password', models.CharField(max_length=255, verbose_name='パスワード')),
                ('create_at', models.DateField(blank=True, default=django.utils.timezone.now, verbose_name='作成日')),
                ('update_at', models.DateField(blank=True, default=django.utils.timezone.now, verbose_name='更新日')),
            ],
        ),
    ]