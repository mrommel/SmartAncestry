# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0024_auto_20150601_1907'),
    ]

    operations = [
        migrations.AddField(
            model_name='familystatusrelation',
            name='date_only_year',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
