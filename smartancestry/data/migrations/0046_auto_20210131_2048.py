# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2021-01-31 19:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0045_auto_20210131_0950'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='table',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='documentrelation',
            name='index',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
