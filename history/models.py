from __future__ import unicode_literals

from django.db import models

class Game(models.Model):
    winner = models.CharField(max_length=200)
    loser = models.CharField(max_length=200)
    gamename = models.CharField(max_length=200)
    created_on = models.DateTimeField('created_on')
    modified_on = models.DateTimeField('modified_on')

    def __str__(self):
        return '{} beat {} at {} on {}'.format(self.winner,self.loser,self.gamename,self.created_on)