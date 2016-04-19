# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0003_season'),
    ]

    operations = [
        migrations.AddField(
            model_name='season',
            name='season_number',
            field=models.IntegerField(default=1),
        ),
    ]
