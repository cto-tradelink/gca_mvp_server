# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-05 13:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0042_auto_20180304_1508'),
    ]

    operations = [
        migrations.AddField(
            model_name='supportbusiness',
            name='icon_set',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='supportbusiness',
            name='pro_0_open',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='supportbusiness',
            name='pro_1_open',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='supportbusiness',
            name='pro_2_open',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='supportbusiness',
            name='short_desc',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
