from datetime import datetime
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from .models import ReturnOrder, Product
import uuid


@receiver(pre_save, sender=ReturnOrder)
def generate_order_number(sender, instance, **kwargs):
    unik_id = str(uuid.uuid4())
    unik_id = "".join(filter(str.isdigit, unik_id))
    now = datetime.now()
    if not instance.identifier:
        instance.identifier = int(now.strftime("%Y%m%d")[2:] + unik_id[-6:])

@receiver(pre_delete, sender=ReturnOrder)
def delete_products_from_opder(sender, instance, **kwargs):
    products = instance.products.all()
    products.delete()