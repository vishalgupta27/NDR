# Generated by Django 4.1.3 on 2023-06-14 07:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0013_rename_lenderrating_lenderreviews_rating_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='lenderreviews',
            name='about_renter',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='lenderreviews',
            name='renterRating',
            field=models.IntegerField(null=True),
        ),
    ]
