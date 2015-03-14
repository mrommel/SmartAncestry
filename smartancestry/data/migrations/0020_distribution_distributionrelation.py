# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0019_ancestryrelation_featured'),
    ]

    operations = [
        migrations.CreateModel(
            name='Distribution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('family_name', models.CharField(max_length=50)),
                ('image', models.ImageField(null=True, upload_to=b'media/distributions', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DistributionRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ancestry', models.ForeignKey(to='data.Ancestry')),
                ('distribution', models.ForeignKey(to='data.Distribution')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
