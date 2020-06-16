# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0006_person_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('city', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=50)),
                ('country', models.CharField(max_length=50)),
                ('lon', models.FloatField(default=0)),
                ('lat', models.FloatField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='person',
            name='birth_location',
            field=models.ForeignKey(related_name='birth_location', on_delete=models.CASCADE, blank=True, to='data.Location', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='death_location',
            field=models.ForeignKey(related_name='death_location', on_delete=models.CASCADE, blank=True, to='data.Location', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person',
            name='image',
            field=models.ImageField(null=True, upload_to=b'data/media/persons', blank=True),
            preserve_default=True,
        ),
    ]
