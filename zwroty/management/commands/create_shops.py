from django.core.management.base import BaseCommand
from zwroty.models import Shop
import xlrd


class Command(BaseCommand):
    help = "Command to create Shops"

    def handle(self, *args, **options):
        current_shops = list(Shop.objects.all().values_list("shop_nr", flat=True))

        workbook = xlrd.open_workbook("shops.xls")
        sheet = workbook.sheet_by_index(0)

        loc_inst = [
            Shop(
                shop_nr=int(sheet.row_values(row)[0]),
                description=str(sheet.row_values(row)[1]),
                ship_doc=str(sheet.row_values(row)[2]),
            )
            for row in range(1, sheet.nrows)
            if str(sheet.row_values(row)[0]) not in current_shops
        ]
        Shop.objects.bulk_create(loc_inst)

        self.stdout.write("Shops was created")
