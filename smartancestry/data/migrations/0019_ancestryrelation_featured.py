# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0018_auto_20150223_1442'),
    ]

    operations = [
        migrations.AddField(
            model_name='ancestryrelation',
            name='featured',
            field=models.NullBooleanField(default=False),
            preserve_default=True,
        ),
    ]
