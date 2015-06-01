# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0023_document_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='birth_date_only_year',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='death_date_only_year',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
