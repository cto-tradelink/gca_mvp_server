# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-25 22:25
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0005_auto_20180925_2153'),
    ]

    operations = [
        migrations.RenameField(
            model_name='hitlog',
            old_name='date',
            new_name='hit_date',
        ),
    ]