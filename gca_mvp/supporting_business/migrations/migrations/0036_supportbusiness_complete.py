# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-01 23:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0035_auto_20180302_0658'),
    ]

    operations = [
        migrations.AddField(
            model_name='supportbusiness',
            name='complete',
            field=models.BooleanField(default=False),
        ),
    ]
