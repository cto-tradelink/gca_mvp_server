# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-02 19:12
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0019_auto_20180702_1900'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hitlog',
            name='date',
            field=models.DateField(blank=True, default=datetime.datetime(2018, 7, 2, 19, 12, 27, 540001), null=True),
        ),
        migrations.AlterField(
            model_name='reply',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supporting_business.Startup'),
        ),
    ]