# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-03 05:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0036_supportbusiness_complete'),
    ]

    operations = [
        migrations.CreateModel(
            name='Award',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('prize', models.CharField(blank=True, max_length=100, null=True)),
                ('update_at', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='supportbusiness',
            name='applicant',
        ),
        migrations.AlterField(
            model_name='appliance',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='award',
            name='sb',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supporting_business.SupportBusiness'),
        ),
        migrations.AddField(
            model_name='award',
            name='startup',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supporting_business.Startup'),
        ),
    ]