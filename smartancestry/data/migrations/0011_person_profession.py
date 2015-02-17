# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0010_auto_20150208_0901'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='profession',
            field=models.CharField(max_length=50, null=True, blank=True),
            preserve_default=True,
        ),
    ]
