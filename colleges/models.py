
# Create your models here.
from django.db import models


class College(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    city = models.CharField(max_length=100)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.name