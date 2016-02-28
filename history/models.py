from __future__ import unicode_literals

from django.db import models

class Game(models.Model):
    winner = models.CharField(max_length=200)
    loser = models.CharField(max_length=200)
    gamename = models.CharField(max_length=200)
    created_on = models.DateTimeField('created_on')
    modified_on = models.DateTimeField('modified_on')

    def __str__(self):
        list_tags = []
        list_message = ""
        for tag in Tag.objects.filter(game=self).values_list('tag', flat=True).distinct():
            list_tags.append(tag)                    
        for name in list(set(list_tags)):
            list_message += "#{} ".format(name)
        return '{} beat {} at {} at {} {}'.format(self.winner,self.loser,self.gamename,self.created_on.strftime('%T, %d %b %Y'), list_message)


class Tag(models.Model):
    tag = models.CharField(max_length=200)
    game = models.ForeignKey(Game)

    def __str__(self):
        return '{} in {}'.format(self.tag, self.game.gamename)
