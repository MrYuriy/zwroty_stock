# Generated by Django 5.0.6 on 2024-05-15 04:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("zwroty", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="skuinformation",
            old_name="sku",
            new_name="sku_log",
        ),
    ]
