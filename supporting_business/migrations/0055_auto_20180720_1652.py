# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-20 16:52
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0054_auto_20180719_1401'),
    ]

    operations = [
        migrations.AddField(
            model_name='appliance',
            name='cert_file',
            field=models.CharField(blank=True, default='', max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='appliance',
            name='patent_2_file',
            field=models.CharField(blank=True, default='', max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='appliance',
            name='service_file',
            field=models.CharField(blank=True, default='', max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='hitlog',
            name='date',
            field=models.DateField(blank=True, default=datetime.datetime(2018, 7, 20, 16, 52, 39, 989000), null=True),
        ),
    ]
