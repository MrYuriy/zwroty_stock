# Generated by Django 4.1.13 on 2024-05-18 19:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Barcode",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("barcode", models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.IntegerField()),
                ("actual_barcode", models.CharField(max_length=20)),
                (
                    "tape_of_delivery",
                    models.CharField(
                        choices=[("P", "Pallet"), ("C", "Box")],
                        default="C",
                        max_length=1,
                        verbose_name="tape_of_delivery",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ReasoneComment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Shop",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("shop_nr", models.IntegerField()),
                ("description", models.CharField(max_length=100)),
                ("ship_doc", models.CharField(max_length=4)),
            ],
        ),
        migrations.CreateModel(
            name="SkuInformation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("sku_log", models.IntegerField()),
                ("sku_hand", models.BigIntegerField(blank=True, null=True)),
                (
                    "name_of_product",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SkuInformationBarcode",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "barcode",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="zwroty.barcode"
                    ),
                ),
                (
                    "sku_information",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="zwroty.skuinformation",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ReturnOrder",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nr_order", models.CharField(max_length=20)),
                ("position_nr", models.IntegerField()),
                ("identifier", models.BigIntegerField(unique=True)),
                ("date_recive", models.DateTimeField(auto_now_add=True)),
                ("comment", models.TextField(blank=True, null=True)),
                ("transaction", models.TextField(blank=True)),
                ("complite_status", models.BooleanField(default=False)),
                ("products", models.ManyToManyField(to="zwroty.product")),
                (
                    "shop",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="zwroty.shop"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="product",
            name="reasone",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="zwroty.reasonecomment"
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="sku",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="zwroty.skuinformation",
            ),
        ),
    ]
