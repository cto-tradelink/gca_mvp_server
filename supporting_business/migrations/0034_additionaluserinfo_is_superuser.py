# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-11-21 14:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0033_supportbusiness_support_business_raw_filter_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='additionaluserinfo',
            name='is_superuser',
            field=models.BooleanField(default=False),
        ),
    ]