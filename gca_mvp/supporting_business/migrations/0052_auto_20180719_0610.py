# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-19 06:10
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0051_auto_20180718_2330'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hitlog',
            name='date',
            field=models.DateField(blank=True, default=datetime.datetime(2018, 7, 19, 6, 10, 2, 141800), null=True),
        ),
    ]
