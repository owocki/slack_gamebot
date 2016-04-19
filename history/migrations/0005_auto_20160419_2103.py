# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def migrate_data(apps, schema_editor):
    Season = apps.get_model('history', 'Season')
    for s in Season.objects.all():
        print(s)
        num_seasons_before = Season.objects.filter(pk__lt=s.pk, gamename=s.gamename).count()
        s.season_number = num_seasons_before + 1
        s.save()


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0004_season_season_number'),
    ]

    operations = [
        migrations.RunPython(migrate_data),
    ]
