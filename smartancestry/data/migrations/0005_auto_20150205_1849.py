# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0004_familystatusrelation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='familystatusrelation',
            name='date',
            field=models.DateField(null=True, verbose_name=b'date of marriage or divorce', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person',
            name='birth_date',
            field=models.DateField(null=True, verbose_name=b'date of birth', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person',
            name='death_date',
            field=models.DateField(null=True, verbose_name=b'date of death', blank=True),
            preserve_default=True,
        ),
    ]
