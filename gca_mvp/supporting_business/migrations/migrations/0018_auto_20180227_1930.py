# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-27 10:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0017_startup_fund_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='supportbusiness',
            name='finace_amount',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='supportbusiness',
            name='apply_num',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='supportbusiness',
            name='hit',
            field=models.IntegerField(default=0),
        ),
    ]
