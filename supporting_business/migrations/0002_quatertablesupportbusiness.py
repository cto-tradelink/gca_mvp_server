# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-25 21:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuaterTableSupportBusiness',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('support_business_author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supporting_business.AdditionalUserInfo')),
            ],
        ),
    ]
