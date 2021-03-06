# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-11 23:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0053_auto_20180311_1822'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alarm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(blank=True, max_length=500, null=True)),
                ('category', models.CharField(blank=True, max_length=2, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('origin_sb', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supporting_business.SupportBusiness')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supporting_business.Startup')),
            ],
        ),
    ]
