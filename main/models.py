import datetime

from django.db import models

from django.utils.timezone import now


# Create your models here.

class Product(models.Model):
    productSku = models.CharField(max_length=255, default="")
    productDescription = models.CharField(max_length=255, default="")
    quantity = models.IntegerField()
    dateAdded = models.DateTimeField(default=now())
    location = models.CharField(max_length=255)
    image = models.ImageField(default=None, null=True, upload_to='images/')
