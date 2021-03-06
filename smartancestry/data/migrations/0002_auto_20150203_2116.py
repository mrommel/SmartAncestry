# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='birth_date',
            field=models.DateTimeField(null=True, verbose_name=b'date of birth', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person',
            name='death_date',
            field=models.DateTimeField(null=True, verbose_name=b'date of death', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='relation',
            name='date',
            field=models.DateTimeField(null=True, verbose_name=b'date', blank=True),
            preserve_default=True,
        ),
    ]
