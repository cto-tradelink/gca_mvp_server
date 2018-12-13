# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-01 19:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0030_auto_20180302_0347'),
    ]

    operations = [
        migrations.AddField(
            model_name='appliance',
            name='business_file',
            field=models.FileField(blank=True, null=True, upload_to='gca/business'),
        ),
        migrations.AddField(
            model_name='appliance',
            name='created_at',
            field=models.DateTimeField(auto_created=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='appliance',
            name='etc_file',
            field=models.FileField(blank=True, null=True, upload_to='gca/etc'),
        ),
        migrations.AddField(
            model_name='appliance',
            name='fund_file',
            field=models.FileField(blank=True, null=True, upload_to='gca/fund'),
        ),
        migrations.AddField(
            model_name='appliance',
            name='ir_file',
            field=models.FileField(blank=True, null=True, upload_to='gca/ir'),
        ),
        migrations.AddField(
            model_name='appliance',
            name='ppt_file',
            field=models.FileField(blank=True, null=True, upload_to='gca/ppt'),
        ),
        migrations.AddField(
            model_name='appliance',
            name='tax_file',
            field=models.FileField(blank=True, null=True, upload_to='gca/tax'),
        ),
        migrations.AddField(
            model_name='appliance',
            name='update_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]