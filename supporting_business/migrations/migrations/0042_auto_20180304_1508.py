# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-04 06:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0041_auto_20180304_1507'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appliance',
            name='etc_file_title',
            field=models.TextField(blank=True, null=True),
        ),
    ]
