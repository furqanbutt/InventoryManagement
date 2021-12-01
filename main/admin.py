from django.contrib import admin

# Register your models here.

from .models import Product, Transaction

admin.site.register(Product)
admin.site.register(Transaction)
