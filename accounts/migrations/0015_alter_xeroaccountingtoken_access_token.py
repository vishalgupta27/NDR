# Generated by Django 4.1.3 on 2023-05-23 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_alter_useravailability_availabilitydate_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='xeroaccountingtoken',
            name='access_token',
            field=models.CharField(blank=True, max_length=5000, null=True),
        ),
    ]
