# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-19 08:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0008_auto_20180215_1230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='startup',
            name='apply',
            field=models.ManyToManyField(blank=True, null=True, to='supporting_business.SupportBusiness'),
        ),
    ]
