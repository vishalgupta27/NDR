# Generated by Django 4.1.3 on 2023-05-02 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_products_product_image_1_products_product_image_3_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderdetails',
            name='sales_month',
            field=models.CharField(default='May', max_length=100),
        ),
    ]
