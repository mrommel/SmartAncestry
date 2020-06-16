# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0002_auto_20150203_2116'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ancestry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AncestryRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ancestry', models.ForeignKey(to='data.Ancestry', on_delete=models.CASCADE)),
                ('person', models.ForeignKey(to='data.Person', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='relation',
            name='persons',
        ),
        migrations.DeleteModel(
            name='Relation',
        ),
        migrations.AddField(
            model_name='person',
            name='father',
            field=models.ForeignKey(related_name='children_father', on_delete=models.CASCADE, blank=True, to='data.Person', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='mother',
            field=models.ForeignKey(related_name='children_mother', on_delete=models.CASCADE, blank=True, to='data.Person', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='notes',
            field=models.CharField(max_length=500, null=True, blank=True),
            preserve_default=True,
        ),
    ]
