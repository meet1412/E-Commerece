# Generated by Django 4.1.5 on 2023-01-18 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shopapp", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="address",
            name="country",
            field=models.CharField(max_length=255, null=True),
        ),
    ]
