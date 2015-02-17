# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('sex', models.CharField(max_length=1, choices=[(b'M', b'Male'), (b'F', b'Female')])),
                ('birth_date', models.DateTimeField(verbose_name=b'date of birth')),
                ('death_date', models.DateTimeField(verbose_name=b'date of death')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Relation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('relation', models.CharField(max_length=1, choices=[(b'C', b'is child of'), (b'M', b'is married to')])),
                ('date', models.DateTimeField(verbose_name=b'date')),
                ('persons', models.ManyToManyField(to='data.Person')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
