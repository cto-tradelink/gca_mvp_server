# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-15 03:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0007_auto_20180214_1036'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='startup',
            name='tag',
        ),
        migrations.AddField(
            model_name='startup',
            name='keyword',
            field=models.CharField(default='', max_length=500),
            preserve_default=False,
        ),
    ]
