# Generated by Django 5.0.1 on 2024-01-13 09:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("image_processing", "0004_frontendevent"),
    ]

    operations = [
        migrations.AlterField(
            model_name="storedimage",
            name="image",
            field=models.ImageField(upload_to="media/uploads/"),
        ),
    ]
