# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-01 18:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0027_auto_20180302_0246'),
    ]

    operations = [
        migrations.AddField(
            model_name='supportbusiness',
            name='choose_method',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='supportbusiness',
            name='constraint',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='supportbusiness',
            name='constraint_tag',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='supportbusiness',
            name='prefer',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='supportbusiness',
            name='prefer_tag',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='supportbusiness',
            name='pro_0_choose',
            field=models.TextField(blank=True, null=True),
        ),
    ]
