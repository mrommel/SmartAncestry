# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2018-12-18 13:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0033_documentancestryrelation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='personeventrelation',
            name='location',
        ),
        migrations.RemoveField(
            model_name='personeventrelation',
            name='person',
        ),
        migrations.DeleteModel(
            name='PersonEventRelation',
        ),
    ]
