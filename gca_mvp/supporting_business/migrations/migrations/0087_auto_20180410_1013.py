# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-10 10:13
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0086_auto_20180410_1013'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='supportbusiness',
            name='confirm_list',
        ),
        migrations.AlterField(
            model_name='hitlog',
            name='date',
            field=models.DateField(blank=True, default=datetime.datetime(2018, 4, 10, 10, 13, 29, 530011), null=True),
        ),
    ]