# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-22 19:42
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0055_auto_20180720_1652'),
    ]

    operations = [
        migrations.AddField(
            model_name='startup',
            name='facebook',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='insta',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='youtube',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='hitlog',
            name='date',
            field=models.DateField(blank=True, default=datetime.datetime(2018, 7, 22, 19, 42, 36, 96000), null=True),
        ),
    ]
