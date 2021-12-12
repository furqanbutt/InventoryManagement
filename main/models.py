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

    def __str__(self):
        return "[%s] %s" % (self.productSku, self.productDescription)


class Transaction(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantityUsed = models.IntegerField()
    dateUsed = models.DateTimeField(default=now())
    type = models.CharField(max_length=255, default="Job")

    def __str__(self):
        return "[%s] %s items used at [%s]." % (self.product.productSku, self.quantityUsed, self.dateUsed.__str__())
