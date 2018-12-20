# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2018-12-20 20:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0037_auto_20181220_1349'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='type',
            field=models.CharField(choices=[(b'P', 'Portrait'), (b'L', 'Landscape')], default=b'L', max_length=1),
        ),
    ]