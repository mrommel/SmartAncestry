# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-07-13 06:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0025_familystatusrelation_date_only_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='name',
            field=models.CharField(max_length=80),
        ),
    ]
