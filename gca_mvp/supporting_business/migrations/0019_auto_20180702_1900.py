# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-02 19:00
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0018_auto_20180702_1656'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='kind',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='hitlog',
            name='date',
            field=models.DateField(blank=True, default=datetime.datetime(2018, 7, 2, 19, 0, 26, 749001), null=True),
        ),
    ]
