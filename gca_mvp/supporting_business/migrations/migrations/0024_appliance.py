# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-01 12:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0023_supportbusiness_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appliance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('business_number', models.CharField(blank=True, max_length=20, null=True)),
                ('industry_category', models.CharField(blank=True, max_length=100, null=True)),
                ('found_date', models.DateField(blank=True, null=True)),
                ('repre_name', models.CharField(blank=True, max_length=100, null=True)),
                ('repre_tel', models.CharField(blank=True, max_length=100, null=True)),
                ('repre_email', models.CharField(blank=True, max_length=100, null=True)),
                ('mark_name', models.CharField(blank=True, max_length=100, null=True)),
                ('mark_tel', models.CharField(blank=True, max_length=100, null=True)),
                ('mark_email', models.CharField(blank=True, max_length=100, null=True)),
                ('website', models.CharField(blank=True, max_length=200, null=True)),
                ('facebook_address', models.CharField(blank=True, max_length=300, null=True)),
                ('insta_address', models.CharField(blank=True, max_length=300, null=True)),
                ('total_employ', models.CharField(blank=True, max_length=20, null=True)),
                ('hold_employ', models.CharField(blank=True, max_length=20, null=True)),
                ('assurance_employ', models.CharField(blank=True, max_length=20, null=True)),
                ('revenue_before_0', models.CharField(blank=True, max_length=20, null=True)),
                ('revenue_before_1', models.CharField(blank=True, max_length=20, null=True)),
                ('revenue_before_2', models.CharField(blank=True, max_length=20, null=True)),
                ('fund_before_0', models.CharField(blank=True, max_length=20, null=True)),
                ('fund_before_1', models.CharField(blank=True, max_length=20, null=True)),
                ('fund_before_2', models.CharField(blank=True, max_length=20, null=True)),
                ('patent', models.CharField(blank=True, max_length=5, null=True)),
                ('trademark', models.CharField(blank=True, max_length=5, null=True)),
                ('patent_2', models.CharField(blank=True, max_length=5, null=True)),
                ('design', models.CharField(blank=True, max_length=5, null=True)),
                ('service_category', models.CharField(blank=True, max_length=200, null=True)),
                ('service_name', models.CharField(blank=True, max_length=100, null=True)),
                ('service_intro', models.TextField(blank=True, null=True)),
                ('oversea', models.CharField(blank=True, max_length=300, null=True)),
                ('oversea_status', models.CharField(blank=True, max_length=300, null=True)),
                ('specification', models.TextField(blank=True, null=True)),
                ('intro', models.TextField(blank=True, null=True)),
                ('detail', models.TextField(blank=True, null=True)),
                ('startup', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='supporting_business.Startup')),
            ],
        ),
    ]