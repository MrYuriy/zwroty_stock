# Generated by Django 5.0.6 on 2024-05-15 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("zwroty", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="tape_of_delivery",
            field=models.CharField(
                choices=[("P", "Pallet"), ("C", "Box")],
                default="C",
                max_length=1,
                verbose_name="tape_of_delivery",
            ),
        ),
    ]
