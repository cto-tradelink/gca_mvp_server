# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-22 16:20
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0074_emailconirmation'),
    ]

    operations = [
        migrations.CreateModel(
            name='HitLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, default=datetime.datetime(2018, 3, 22, 16, 20, 7, 30200), null=True)),
                ('sb', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supporting_business.SupportBusiness')),
            ],
        ),
    ]
