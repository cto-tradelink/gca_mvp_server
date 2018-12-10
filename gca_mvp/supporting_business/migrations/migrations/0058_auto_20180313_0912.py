# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-13 09:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0057_auto_20180312_1139'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fund',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.CharField(blank=True, max_length=5, null=True)),
                ('size', models.CharField(blank=True, max_length=10, null=True)),
                ('agency', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Revenue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.CharField(blank=True, max_length=5, null=True)),
                ('size', models.CharField(blank=True, max_length=10, null=True)),
            ],
        ),
        migrations.RenameField(
            model_name='startup',
            old_name='address',
            new_name='address_0',
        ),
        migrations.AddField(
            model_name='startup',
            name='address_0_title',
            field=models.CharField(blank=True, default='', max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='address_1',
            field=models.CharField(blank=True, default='', max_length=400, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='address_1_title',
            field=models.CharField(blank=True, default='', max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='address_2',
            field=models.CharField(blank=True, default='', max_length=400, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='address_2_title',
            field=models.CharField(blank=True, default='', max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='address_detail_0',
            field=models.CharField(blank=True, default='', max_length=400, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='address_detail_1',
            field=models.CharField(blank=True, default='', max_length=400, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='address_detail_2',
            field=models.CharField(blank=True, default='', max_length=400, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='export_before_0',
            field=models.CharField(blank=True, default='', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='export_before_1',
            field=models.CharField(blank=True, default='', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='export_before_2',
            field=models.CharField(blank=True, default='', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='export_before_year_0',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='export_before_year_1',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='export_before_year_2',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='fund_before_0',
            field=models.CharField(blank=True, default='', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='fund_before_1',
            field=models.CharField(blank=True, default='', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='fund_before_2',
            field=models.CharField(blank=True, default='', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='fund_before_3',
            field=models.CharField(blank=True, default='', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='fund_before_4',
            field=models.CharField(blank=True, default='', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='fund_before_5',
            field=models.CharField(blank=True, default='', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='fund_before_6',
            field=models.CharField(blank=True, default='', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='fund_before_7',
            field=models.CharField(blank=True, default='', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='fund_before_8',
            field=models.CharField(blank=True, default='', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='fund_before_9',
            field=models.CharField(blank=True, default='', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='fund_before_year_0',
            field=models.CharField(blank=True, max_length=13, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='fund_before_year_1',
            field=models.CharField(blank=True, max_length=13, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='fund_before_year_2',
            field=models.CharField(blank=True, max_length=13, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='fund_before_year_3',
            field=models.CharField(blank=True, max_length=13, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='fund_before_year_4',
            field=models.CharField(blank=True, max_length=13, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='fund_before_year_5',
            field=models.CharField(blank=True, max_length=13, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='fund_before_year_6',
            field=models.CharField(blank=True, max_length=13, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='fund_before_year_7',
            field=models.CharField(blank=True, max_length=13, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='fund_before_year_8',
            field=models.CharField(blank=True, max_length=13, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='fund_before_year_9',
            field=models.CharField(blank=True, max_length=13, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='revenue_before_0',
            field=models.CharField(blank=True, default='', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='revenue_before_1',
            field=models.CharField(blank=True, default='', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='revenue_before_2',
            field=models.CharField(blank=True, default='', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='revenue_before_year_0',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='revenue_before_year_1',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
        migrations.AddField(
            model_name='startup',
            name='revenue_before_year_2',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
        migrations.AddField(
            model_name='revenue',
            name='startup',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supporting_business.Startup'),
        ),
        migrations.AddField(
            model_name='fund',
            name='startup',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supporting_business.Startup'),
        ),
    ]
