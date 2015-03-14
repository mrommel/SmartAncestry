# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0020_distribution_distributionrelation'),
    ]

    operations = [
        migrations.AddField(
            model_name='ancestry',
            name='map',
            field=models.ImageField(null=True, upload_to=b'media/maps', blank=True),
            preserve_default=True,
        ),
    ]
