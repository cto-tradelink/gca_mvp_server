# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-19 04:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0069_supportbusiness_confirm'),
    ]

    operations = [
        migrations.AddField(
            model_name='additionaluserinfo',
            name='phone',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
    ]
