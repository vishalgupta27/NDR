# Generated by Django 4.1.3 on 2023-07-04 05:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0027_delete_lendersstripeaccount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useravailability',
            name='availabilityDate',
            field=models.JSONField(blank=True, null=True),
        ),
    ]