# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-10 10:13
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0087_auto_20180410_1013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hitlog',
            name='date',
            field=models.DateField(blank=True, default=datetime.datetime(2018, 4, 10, 10, 13, 33, 766011), null=True),
        ),
    ]
