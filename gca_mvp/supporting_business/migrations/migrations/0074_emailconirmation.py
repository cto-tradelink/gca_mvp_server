# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-21 15:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0073_auto_20180321_1110'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailConirmation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=300)),
                ('confirmation_code', models.CharField(max_length=300)),
            ],
        ),
    ]