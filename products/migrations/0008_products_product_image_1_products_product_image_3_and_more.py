# Generated by Django 4.1.3 on 2023-04-27 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_alter_unavailabilitydate_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='Product_Image_1',
            field=models.ImageField(blank=True, null=True, upload_to='user/Products_IMG'),
        ),
        migrations.AddField(
            model_name='products',
            name='Product_Image_3',
            field=models.ImageField(blank=True, null=True, upload_to='user/Products_IMG'),
        ),
        migrations.AddField(
            model_name='products',
            name='Product_Image_4',
            field=models.ImageField(blank=True, null=True, upload_to='user/Products_IMG'),
        ),
        migrations.AddField(
            model_name='products',
            name='Product_Image_5',
            field=models.ImageField(blank=True, null=True, upload_to='user/Products_IMG'),
        ),
    ]