# Generated by Django 4.1.3 on 2023-06-13 05:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_productpickupreturn_renter_pickup_location_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='lenderreviews',
            old_name='rating',
            new_name='lenderRating',
        ),
        migrations.AddField(
            model_name='lenderreviews',
            name='productRating',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='orderdetails',
            name='sales_month',
            field=models.CharField(default='June', max_length=100),
        ),
        migrations.AlterField(
            model_name='productpickupreturn',
            name='lender_pickUp_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='productpickupreturn',
            name='lender_return_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='productpickupreturn',
            name='renter_pickUp_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='productpickupreturn',
            name='renter_return_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
