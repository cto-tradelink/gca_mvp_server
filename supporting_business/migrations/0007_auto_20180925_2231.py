# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-25 22:31
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0006_auto_20180925_2225'),
    ]

    operations = [
        migrations.RenameField(
            model_name='hitlog',
            old_name='hit_date',
            new_name='date',
        ),
    ]