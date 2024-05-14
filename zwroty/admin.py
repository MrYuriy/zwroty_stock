from django.contrib import admin

from django.contrib import admin
from .models import Shop, SkuInformation, Barcode, Product, ReasoneComment, ReturnOrder

# Register your models here
admin.site.register(Shop)
admin.site.register(SkuInformation)
admin.site.register(Barcode)
admin.site.register(Product)
admin.site.register(ReasoneComment)
admin.site.register(ReturnOrder)

