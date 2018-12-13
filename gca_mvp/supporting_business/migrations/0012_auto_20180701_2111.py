# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-01 21:11
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0011_auto_20180627_1044'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('text', models.TextField()),
                ('startup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supporting_business.Startup')),
            ],
        ),
        migrations.CreateModel(
            name='ActivityLike',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('like_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supporting_business.Activity')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supporting_business.AdditionalUserInfo')),
            ],
        ),
        migrations.CreateModel(
            name='Reply',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supporting_business.Activity')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supporting_business.AdditionalUserInfo')),
            ],
        ),
        migrations.CreateModel(
            name='TradeInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.CharField(blank=True, max_length=5, null=True)),
                ('size', models.CharField(blank=True, max_length=10, null=True)),
                ('startup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supporting_business.Startup')),
            ],
        ),
        migrations.AddField(
            model_name='fund',
            name='currency',
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
        migrations.AddField(
            model_name='fund',
            name='step',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='hitlog',
            name='date',
            field=models.DateField(blank=True, default=datetime.datetime(2018, 7, 1, 21, 11, 8, 242001), null=True),
        ),
    ]