from django.db import models
from django.contrib.auth.models import User

class Pokemon(models.Model):
    name = models.CharField(unique=True, max_length=64)
    p_id = models.IntegerField(unique=True)
    favourite = models.ManyToManyField(User, related_name='favourites', blank=True)
    
    def __str__(self):
        return f'{self.p_id} - {self.name}'
