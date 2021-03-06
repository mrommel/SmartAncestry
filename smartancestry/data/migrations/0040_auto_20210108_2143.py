# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-01-08 20:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0039_auto_20201230_2050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ancestryrelation',
            name='ancestry',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='data.Ancestry'),
        ),
        migrations.AlterField(
            model_name='ancestryrelation',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='data.Person'),
        ),
        migrations.AlterField(
            model_name='distributionrelation',
            name='ancestry',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='data.Ancestry'),
        ),
        migrations.AlterField(
            model_name='distributionrelation',
            name='distribution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='data.Distribution'),
        ),
        migrations.AlterField(
            model_name='documentancestryrelation',
            name='ancestry',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='data.Ancestry'),
        ),
        migrations.AlterField(
            model_name='documentancestryrelation',
            name='document',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='data.Document'),
        ),
        migrations.AlterField(
            model_name='documentrelation',
            name='document',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='data.Document'),
        ),
        migrations.AlterField(
            model_name='documentrelation',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='data.Person'),
        ),
        migrations.AlterField(
            model_name='familystatusrelation',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='data.Location'),
        ),
        migrations.AlterField(
            model_name='familystatusrelation',
            name='man',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='Ehemann', to='data.Person'),
        ),
        migrations.AlterField(
            model_name='familystatusrelation',
            name='woman',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='Ehefrau', to='data.Person'),
        ),
        migrations.AlterField(
            model_name='person',
            name='birth_location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='birth_location', to='data.Location'),
        ),
        migrations.AlterField(
            model_name='person',
            name='death_location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='death_location', to='data.Location'),
        ),
        migrations.AlterField(
            model_name='person',
            name='father',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='children_father', to='data.Person'),
        ),
        migrations.AlterField(
            model_name='person',
            name='mother',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='children_mother', to='data.Person'),
        ),
        migrations.AlterField(
            model_name='personevent',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='data.Location'),
        ),
        migrations.AlterField(
            model_name='personevent',
            name='person',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='data.Person'),
        ),
        migrations.AlterField(
            model_name='question',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='data.Person'),
        ),
    ]
