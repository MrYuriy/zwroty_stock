from .models import Barcode, SkuInformation, SkuInformationBarcode
from typing import Optional

def get_or_create_sku(
        ean: str, sku_description: Optional[str]=None
        ) -> SkuInformation:
    
    sku_inform_bar = SkuInformationBarcode.objects.filter(
            barcode__barcode__icontains=ean
        )
    
    if sku_inform_bar and ean != "999999999999" :
        # if fing more one sku try got sku wit sku_hand
        if len(sku_inform_bar)>1:
            sku_inform_bar_hand=sku_inform_bar.filter(
                sku_information__sku_hand__isnull=False
                )
            if sku_inform_bar_hand:
                sku_inform_bar = sku_inform_bar_hand
        sku = sku_inform_bar[0].sku_information
    else:
        sku = None

    if not sku:
            print(ean)
            barcode, _ = Barcode.objects.get_or_create(barcode=ean)

            description = ""
            if sku_description:
                description = sku_description
                
            sku = SkuInformation(
                sku_log=ean,name_of_product=description
            )

            sku.save()
            sku_inform_barcode = SkuInformationBarcode(
                barcode = barcode,
                sku_information = sku
            )
            sku_inform_barcode.save()
    return (sku)