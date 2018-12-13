# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-01 21:36
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0014_auto_20180701_2123'),
    ]

    operations = [
        migrations.AddField(
            model_name='history',
            name='startup',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='supporting_business.Startup'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='hitlog',
            name='date',
            field=models.DateField(blank=True, default=datetime.datetime(2018, 7, 1, 21, 36, 2, 557001), null=True),
        ),
    ]