# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-11-20 12:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0031_auto_20181119_1839'),
    ]

    operations = [
        migrations.CreateModel(
            name='SupportBusinessAttachedFiles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_path', models.CharField(blank=True, max_length=500, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='supportbusiness',
            name='all_filter',
        ),
        migrations.RemoveField(
            model_name='supportbusiness',
            name='all_line_data',
        ),
        migrations.RemoveField(
            model_name='supportbusiness',
            name='all_startup_list',
        ),
        migrations.RemoveField(
            model_name='supportbusiness',
            name='applied_filter',
        ),
        migrations.RemoveField(
            model_name='supportbusiness',
            name='applied_line_data',
        ),
        migrations.RemoveField(
            model_name='supportbusiness',
            name='applied_startup_list',
        ),
        migrations.RemoveField(
            model_name='supportbusiness',
            name='awarded_filter',
        ),
        migrations.RemoveField(
            model_name='supportbusiness',
            name='awarded_line_data',
        ),
        migrations.RemoveField(
            model_name='supportbusiness',
            name='awarded_startup_list',
        ),
        migrations.RemoveField(
            model_name='supportbusiness',
            name='fav_filter',
        ),
        migrations.RemoveField(
            model_name='supportbusiness',
            name='fav_line_data',
        ),
        migrations.RemoveField(
            model_name='supportbusiness',
            name='fav_startup_list',
        ),
        migrations.RemoveField(
            model_name='supportbusiness',
            name='hit_filter',
        ),
        migrations.RemoveField(
            model_name='supportbusiness',
            name='hit_line_data',
        ),
        migrations.RemoveField(
            model_name='supportbusiness',
            name='hit_startup_list',
        ),
        migrations.AddField(
            model_name='supportbusinessattachedfiles',
            name='support_business',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supporting_business.SupportBusiness'),
        ),
    ]
