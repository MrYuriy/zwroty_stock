from django.conf import settings
from django.db import models


class Shop(models.Model):
    shop_nr = models.IntegerField()
    description  = models.CharField(max_length=100)
    ship_doc = models.CharField(max_length=4)

    def __str__(self) -> str:
        return f"{self.shop_nr} - {self.description}"


class SkuInformation(models.Model):
    sku_log = models.IntegerField()
    sku_hand = models.IntegerField(default=0)
    name_of_product = models.CharField(max_length=100)
    barcodes = models.ManyToManyField("Barcode")

    def __str__(self):
        return f"{self.sku_log} {self.name_of_product}"


class Barcode(models.Model):
    barcode = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.barcode



class ReasoneComment(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name



class Product(models.Model):
    PALLET = "P"
    BOX = "C"
    
    TAPE_OF_DELIVERY_CHOICES = [
        (PALLET, "Pallet"),
        (BOX, "Box"),
    ]
    sku = models.ForeignKey("SkuInformation", on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()

    tape_of_delivery = models.CharField(
        max_length=1,
        choices=TAPE_OF_DELIVERY_CHOICES,
        default=BOX,
        verbose_name="tape_of_delivery",
    )
    reasone = models.ForeignKey(ReasoneComment, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.sku.name_of_product


class ReturnOrder(models.Model):
    nr_order = models.CharField(max_length=20)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    products = models.ForeignKey(
        Product, on_delete=models.CASCADE, null=True, blank=True)
    
    identifier = models.BigIntegerField(unique=True)
    date_recive = models.DateTimeField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField()
    transaction = models.TextField(blank=True)
    complite_status = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return f"{self.nr_order} - {self.shop}"
    