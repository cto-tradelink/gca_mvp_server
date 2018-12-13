# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-18 23:30
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0050_auto_20180717_1027'),
    ]

    operations = [
        migrations.AddField(
            model_name='supportbusiness',
            name='open_method',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='hitlog',
            name='date',
            field=models.DateField(blank=True, default=datetime.datetime(2018, 7, 18, 23, 30, 34, 778800), null=True),
        ),
    ]