# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-10 10:28
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0088_auto_20180410_1013'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='additionaluserinfo',
            name='parent',
        ),
        migrations.AlterField(
            model_name='hitlog',
            name='date',
            field=models.DateField(blank=True, default=datetime.datetime(2018, 4, 10, 10, 28, 45, 560011), null=True),
        ),
    ]
