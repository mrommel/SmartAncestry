# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0016_auto_20150211_0620'),
    ]

    operations = [
        migrations.AlterField(
            model_name='familystatusrelation',
            name='man',
            field=models.ForeignKey(related_name='husband', blank=True, to='data.Person', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='familystatusrelation',
            name='woman',
            field=models.ForeignKey(related_name='wife', blank=True, to='data.Person', null=True),
            preserve_default=True,
        ),
    ]
