# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-07 20:20
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0084_auto_20180406_1659'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hitlog',
            name='date',
            field=models.DateField(blank=True, default=datetime.datetime(2018, 4, 7, 20, 20, 47, 780600), null=True),
        ),
    ]
