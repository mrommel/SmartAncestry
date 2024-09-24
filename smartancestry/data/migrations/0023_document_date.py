# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
# from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0022_document_documentrelation'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='date',
            field=models.DateField(default=datetime.datetime(2015, 5, 25, 13, 11, 6, 459347, tzinfo=datetime.timezone.utc), verbose_name=b'date of creation'),
            preserve_default=False,
        ),
    ]
