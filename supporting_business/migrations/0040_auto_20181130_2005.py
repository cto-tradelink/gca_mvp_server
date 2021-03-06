# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-11-30 20:05
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0039_auto_20181130_2001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='countingfilterlisttable',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2018, 11, 30, 20, 5, 32, 480000)),
        ),
        migrations.AlterField(
            model_name='countingstartuplisttable',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2018, 11, 30, 20, 5, 32, 480000)),
        ),
        migrations.AlterField(
            model_name='countingtable',
            name='apply_num',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='countingtable',
            name='fav_num',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='countingtable',
            name='hit_num',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='countingtable',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2018, 11, 30, 20, 5, 32, 479000)),
        ),
        migrations.AlterField(
            model_name='oprendcountingfilterlisttable',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2018, 11, 30, 20, 5, 32, 484000)),
        ),
        migrations.AlterField(
            model_name='oprendcountingstartuplisttable',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2018, 11, 30, 20, 5, 32, 483000)),
        ),
        migrations.AlterField(
            model_name='oprendcountingtable',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2018, 11, 30, 20, 5, 32, 483000)),
        ),
        migrations.AlterField(
            model_name='opringcountingfilterlisttable',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2018, 11, 30, 20, 5, 32, 482000)),
        ),
        migrations.AlterField(
            model_name='opringcountingstartuplisttable',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2018, 11, 30, 20, 5, 32, 481000)),
        ),
        migrations.AlterField(
            model_name='opringcountingtable',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2018, 11, 30, 20, 5, 32, 481000)),
        ),
    ]
