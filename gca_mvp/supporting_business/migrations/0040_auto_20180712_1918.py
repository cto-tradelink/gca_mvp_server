# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-12 19:18
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0039_auto_20180712_1913'),
    ]

    operations = [
        migrations.AddField(
            model_name='path',
            name='object',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='hitlog',
            name='date',
            field=models.DateField(blank=True, default=datetime.datetime(2018, 7, 12, 19, 18, 8, 482400), null=True),
        ),
    ]
