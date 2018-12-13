# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-14 12:53
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('supporting_business', '0044_auto_20180714_0942'),
    ]

    operations = [
        migrations.CreateModel(
            name='WatchLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clip', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='supporting_business.Clip')),
            ],
        ),
        migrations.AddField(
            model_name='additionaluserinfo',
            name='interest_clip',
            field=models.ManyToManyField(blank=True, null=True, to='supporting_business.Clip'),
        ),
        migrations.AddField(
            model_name='additionaluserinfo',
            name='interest_course',
            field=models.ManyToManyField(blank=True, null=True, to='supporting_business.Course'),
        ),
        migrations.AddField(
            model_name='additionaluserinfo',
            name='interest_path',
            field=models.ManyToManyField(blank=True, null=True, to='supporting_business.Path'),
        ),
        migrations.AlterField(
            model_name='appliance',
            name='update_at',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='filter',
            field=models.ManyToManyField(blank=True, null=True, to='supporting_business.EduFilter'),
        ),
        migrations.AlterField(
            model_name='hitlog',
            name='date',
            field=models.DateField(blank=True, default=datetime.datetime(2018, 7, 14, 12, 53, 50, 650403), null=True),
        ),
        migrations.AlterField(
            model_name='path',
            name='filter',
            field=models.ManyToManyField(blank=True, null=True, to='supporting_business.EduFilter'),
        ),
        migrations.AddField(
            model_name='watchlog',
            name='course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='supporting_business.Course'),
        ),
        migrations.AddField(
            model_name='watchlog',
            name='path',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='supporting_business.Path'),
        ),
        migrations.AddField(
            model_name='watchlog',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supporting_business.AdditionalUserInfo'),
        ),
    ]