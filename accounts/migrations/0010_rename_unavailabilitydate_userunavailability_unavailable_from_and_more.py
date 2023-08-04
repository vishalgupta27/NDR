# Generated by Django 4.1.3 on 2023-05-05 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_userunavailability'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userunavailability',
            old_name='UnavailabilityDate',
            new_name='unavailable_from',
        ),
        migrations.AddField(
            model_name='userunavailability',
            name='unavailable_to',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
