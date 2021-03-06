# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-12 14:29
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0032_auto_20180711_0910'),
    ]

    operations = [
        migrations.CreateModel(
            name='Clip',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200, null=True)),
                ('youtube', models.CharField(blank=True, max_length=100, null=True)),
                ('mov_address', models.CharField(blank=True, max_length=200, null=True)),
                ('object', models.CharField(blank=True, max_length=300, null=True)),
                ('info', models.TextField()),
                ('play', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200, null=True)),
                ('object', models.CharField(blank=True, max_length=300, null=True)),
                ('info', models.TextField()),
                ('total_play', models.IntegerField(blank=True, null=True)),
                ('clips', models.ManyToManyField(to='supporting_business.Clip')),
            ],
        ),
        migrations.CreateModel(
            name='EduFilter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Path',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200, null=True)),
                ('object', models.CharField(blank=True, max_length=300, null=True)),
                ('info', models.TextField()),
                ('total_play', models.IntegerField(blank=True, null=True)),
                ('course', models.ManyToManyField(to='supporting_business.Course')),
                ('filter', models.ManyToManyField(to='supporting_business.EduFilter')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supporting_business.AdditionalUserInfo')),
            ],
        ),
        migrations.AlterField(
            model_name='hitlog',
            name='date',
            field=models.DateField(blank=True, default=datetime.datetime(2018, 7, 12, 14, 29, 42, 127400), null=True),
        ),
        migrations.AddField(
            model_name='course',
            name='filter',
            field=models.ManyToManyField(to='supporting_business.EduFilter'),
        ),
        migrations.AddField(
            model_name='course',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supporting_business.AdditionalUserInfo'),
        ),
        migrations.AddField(
            model_name='clip',
            name='filter',
            field=models.ManyToManyField(to='supporting_business.EduFilter'),
        ),
        migrations.AddField(
            model_name='clip',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supporting_business.AdditionalUserInfo'),
        ),
    ]
