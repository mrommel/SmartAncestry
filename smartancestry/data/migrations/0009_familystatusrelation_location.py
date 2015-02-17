# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0008_auto_20150207_2019'),
    ]

    operations = [
        migrations.AddField(
            model_name='familystatusrelation',
            name='location',
            field=models.ForeignKey(blank=True, to='data.Location', null=True),
            preserve_default=True,
        ),
    ]
