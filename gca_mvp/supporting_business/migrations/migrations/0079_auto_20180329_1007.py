# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-29 10:07
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0078_auto_20180328_0431'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hitlog',
            name='date',
            field=models.DateField(blank=True, default=datetime.datetime(2018, 3, 29, 10, 7, 57, 740200), null=True),
        ),
    ]
