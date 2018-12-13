# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-12 19:20
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0040_auto_20180712_1918'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='object',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='hitlog',
            name='date',
            field=models.DateField(blank=True, default=datetime.datetime(2018, 7, 12, 19, 20, 22, 373400), null=True),
        ),
    ]