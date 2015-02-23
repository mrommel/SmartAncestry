# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0017_auto_20150211_0623'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='already_died',
            field=models.NullBooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='familystatusrelation',
            name='status',
            field=models.CharField(max_length=1, choices=[(b'M', b'Marriage'), (b'D', b'Divorce'), (b'P', b'Partnership')]),
            preserve_default=True,
        ),
    ]
