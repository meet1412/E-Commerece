# Generated by Django 4.1.5 on 2023-01-20 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shopapp", "0005_alter_order_orderplaced_alter_order_orderplaceddate"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="orderPlacedtime",
            field=models.CharField(default="13:14 PM", max_length=50),
        ),
    ]
