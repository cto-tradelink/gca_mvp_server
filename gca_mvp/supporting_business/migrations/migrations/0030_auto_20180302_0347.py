# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-01 18:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0029_auto_20180302_0339'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='supportbusiness',
            name='abstract',
        ),
        migrations.RemoveField(
            model_name='supportbusiness',
            name='apply_method',
        ),
        migrations.RemoveField(
            model_name='supportbusiness',
            name='apply_num',
        ),
        migrations.RemoveField(
            model_name='supportbusiness',
            name='author',
        ),
        migrations.RemoveField(
            model_name='supportbusiness',
            name='createdate',
        ),
        migrations.RemoveField(
            model_name='supportbusiness',
            name='detail',
        ),
        migrations.RemoveField(
            model_name='supportbusiness',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='supportbusiness',
            name='from_date',
        ),
        migrations.RemoveField(
            model_name='supportbusiness',
            name='open_date',
        ),
        migrations.RemoveField(
            model_name='supportbusiness',
            name='target',
        ),
        migrations.AddField(
            model_name='supportbusiness',
            name='additional_faq',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='supportbusiness',
            name='ceremony_end',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='supportbusiness',
            name='ceremony_start',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='supportbusiness',
            name='created_at',
            field=models.DateTimeField(auto_created=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='supportbusiness',
            name='faq',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='supportbusiness',
            name='faq_tag',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='supportbusiness',
            name='meta_data',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='supportbusiness',
            name='open_status',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='supportbusiness',
            name='update_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='supportbusiness',
            name='etc',
            field=models.TextField(blank=True, null=True),
        ),
    ]