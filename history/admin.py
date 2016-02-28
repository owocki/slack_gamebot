from django.contrib import admin

from .models import Game
from .models import Tag

admin.site.register(Game)
admin.site.register(Tag)
