# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-27 13:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0019_auto_20180227_1930'),
    ]

    operations = [
        migrations.AddField(
            model_name='supportbusiness',
            name='interest',
            field=models.ManyToManyField(blank=True, null=True, to='supporting_business.Startup'),
        ),
    ]
