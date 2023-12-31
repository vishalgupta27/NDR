# Generated by Django 4.1.3 on 2023-07-03 05:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0019_alter_orderdetails_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderdetails',
            name='payment_status',
            field=models.CharField(choices=[('Paid', 'Paid'), ('Failed', 'Failed'), ('Pending', 'Pending'), ('Refund', 'Refund')], default='Pending', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='orderdetails',
            name='sales_month',
            field=models.CharField(default='July', max_length=100),
        ),
    ]
