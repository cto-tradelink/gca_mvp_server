# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-14 10:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0061_auto_20180314_1050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supportbusiness',
            name='employee_lt_gt',
            field=models.CharField(blank=True, default='제한없음', max_length=4, null=True),
        ),
    ]
