from django.db import models

class Pokemon(models.Model):
    name = models.CharField(unique=True, max_length=64)
    p_id = models.IntegerField(unique=True)
    def __str__(self):
        return self.name
