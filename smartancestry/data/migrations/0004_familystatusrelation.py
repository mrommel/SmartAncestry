# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0003_auto_20150204_1940'),
    ]

    operations = [
        migrations.CreateModel(
            name='FamilyStatusRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(max_length=1, choices=[(b'M', b'Marriage'), (b'D', b'Divorce')])),
                ('date', models.DateTimeField(null=True, verbose_name=b'date of marriage or divorce', blank=True)),
                ('man', models.ForeignKey(related_name='husband', on_delete=models.CASCADE, to='data.Person')),
                ('woman', models.ForeignKey(related_name='wife', on_delete=models.CASCADE, to='data.Person')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
