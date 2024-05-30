import json
from django.core.management.base import BaseCommand
from zwroty.models import SkuInformation, Barcode, SkuInformationBarcode
from tqdm import tqdm
from django.db import transaction
from itertools import islice
from sort_json import sort_sku_path


class Command(BaseCommand):
    help = "Import data from export.json"

    def handle(self, *args, **options):
        file_path = sort_sku_path("sku_barcode.json")

        data = self.load_data(file_path)
        barcode_list, sku_inform_dict = self.process_data(data)

        with transaction.atomic():
            self.bulk_create_barcode(barcode_list)
            self.bulk_create_sku_information(sku_inform_dict)
            self.bulk_create_sku_information_barcode(sku_inform_dict)

        self.stdout.write(self.style.SUCCESS("Successfully imported data"))

    def load_data(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)["items"]

    def process_data(self, data):
        barcode_list = []
        sku_inform_dict = {}
        exist_barcode = set()

        for item in tqdm(data, total=len(data), unit="row"):
            sku_log = int(item["sku_log"])
            sku_hand = item.get("sku_handl", None)
            description = item.get("description", "")
            ean = item["ean"]

            if ean in exist_barcode:
                continue
            exist_barcode.add(ean)

            sku_inst = SkuInformation(
                sku_log=sku_log, sku_hand=sku_hand, name_of_product=description
            )
            bar_cod_inst = Barcode(barcode=ean)
            barcode_list.append(bar_cod_inst)

            if sku_log not in sku_inform_dict:
                sku_inform_dict[sku_log] = {
                    "barcodes": [],
                    "sku_instance": None,
                }

            sku_inform_dict[sku_log]["barcodes"].append(bar_cod_inst)
            sku_inform_dict[sku_log]["sku_instance"] = sku_inst

        return barcode_list, sku_inform_dict

    def chunked_dict(self, d, chunk_size):
        iter_list = iter(d)
        for _ in range(0, len(d), chunk_size):
            yield {key: d[key] for key in islice(iter_list, chunk_size)}
    
    def bulk_create_barcode(self, barcode_list, chunk_size=10000):
        iter_list = iter(barcode_list)
        sliced_barcode_list = [
            list(islice(iter_list, chunk_size))
            for _ in range(0, len(barcode_list), chunk_size)
        ]
        for sub_list in tqdm(sliced_barcode_list, total=len(sliced_barcode_list), unit="barcode"):
            Barcode.objects.bulk_create(sub_list)

    def bulk_create_sku_information(self, sku_inform_dict, chunk_size=10000):
        for chunk in tqdm(
            self.chunked_dict(sku_inform_dict, chunk_size), desc="Create sku_inst"
        ):
            SkuInformation.objects.bulk_create(
                [item["sku_instance"] for item in chunk.values()]
            )

    def bulk_create_sku_information_barcode(self, sku_inform_dict, chunk_size=10000):
        sku_information_barcode_list = []
        for sku_log in tqdm(
            sku_inform_dict, total=len(sku_inform_dict), unit="sku"
        ):
            sku_info = sku_inform_dict[sku_log]
            for barcode in sku_info["barcodes"]:
                sku_information_barcode = SkuInformationBarcode(
                    sku_information=sku_info["sku_instance"], barcode=barcode
                )
                sku_information_barcode_list.append(sku_information_barcode)

        iter_list = iter(sku_information_barcode_list)
        sliced_sku_barcode_list = [
            list(islice(iter_list, chunk_size))
            for _ in range(0, len(sku_information_barcode_list), chunk_size)
        ]
        for sub_list in tqdm(sliced_sku_barcode_list, total=len(sliced_sku_barcode_list), unit="sku_barcode"):
            SkuInformationBarcode.objects.bulk_create(sub_list)
