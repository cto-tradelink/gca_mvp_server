# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-02 20:09
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0020_auto_20180702_1912'),
    ]

    operations = [
        migrations.AddField(
            model_name='startup',
            name='business_file',
            field=models.CharField(blank=True, default='', max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='hitlog',
            name='date',
            field=models.DateField(blank=True, default=datetime.datetime(2018, 7, 2, 20, 9, 46, 239001), null=True),
        ),
    ]
