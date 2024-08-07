from django.contrib import admin

from django.contrib import admin
from .models import (
    Shop, SkuInformation, 
    Barcode, Product, 
    ReasoneComment, ReturnOrder
    )

class ReturnOrderAdmin(admin.ModelAdmin):
    list_display = (
        "identifier", 
        "date_recive", 
        "complite_status", 
        "generate_xls_status",
        )

# Register your models here
admin.site.register(Shop)
admin.site.register(SkuInformation)
admin.site.register(Barcode)
admin.site.register(Product)
admin.site.register(ReasoneComment)
admin.site.register(ReturnOrder, ReturnOrderAdmin)
