# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-25 08:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0013_auto_20180225_1724'),
    ]

    operations = [
        migrations.AlterField(
            model_name='startup',
            name='filter',
            field=models.ManyToManyField(blank=True, null=True, to='supporting_business.Filter'),
        ),
        migrations.AlterField(
            model_name='startup',
            name='tag',
            field=models.ManyToManyField(blank=True, null=True, to='supporting_business.Tag'),
        ),
    ]
