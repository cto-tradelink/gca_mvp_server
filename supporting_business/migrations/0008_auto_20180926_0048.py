# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-26 00:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0007_auto_20180925_2231'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hitlog',
            name='date',
            field=models.DateField(auto_now_add=True),
        ),
    ]
