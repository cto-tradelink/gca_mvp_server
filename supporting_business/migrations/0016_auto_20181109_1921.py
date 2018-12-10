# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-11-09 19:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0015_auto_20181107_2121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appliance',
            name='company_facebook',
            field=models.CharField(blank=True, default='', max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='appliance',
            name='company_instagram',
            field=models.CharField(blank=True, default='', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='appliance',
            name='company_youtube',
            field=models.CharField(blank=True, default='', max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='startup',
            name='company_facebook',
            field=models.CharField(blank=True, default='', max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='startup',
            name='company_instagram',
            field=models.CharField(blank=True, default='', max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='startup',
            name='company_youtube',
            field=models.CharField(blank=True, default='', max_length=300, null=True),
        ),
    ]
