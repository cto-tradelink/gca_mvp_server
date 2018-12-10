# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-11 09:10
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0031_auto_20180711_0909'),
    ]

    operations = [
        migrations.AddField(
            model_name='supportbusiness',
            name='step',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='hitlog',
            name='date',
            field=models.DateField(blank=True, default=datetime.datetime(2018, 7, 11, 9, 10, 27, 762000), null=True),
        ),
    ]
