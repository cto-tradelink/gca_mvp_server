# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-13 13:01
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0041_auto_20180712_1920'),
    ]

    operations = [
        migrations.AddField(
            model_name='additionaluserinfo',
            name='facebook',
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
        migrations.AddField(
            model_name='additionaluserinfo',
            name='twitter',
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='hitlog',
            name='date',
            field=models.DateField(blank=True, default=datetime.datetime(2018, 7, 13, 13, 1, 20, 610600), null=True),
        ),
    ]
