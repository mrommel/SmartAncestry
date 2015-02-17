# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0014_location_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='ancestry',
            name='image',
            field=models.ImageField(null=True, upload_to=b'media/ancestries', blank=True),
            preserve_default=True,
        ),
    ]
