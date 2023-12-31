# Generated by Django 4.1.3 on 2023-06-15 07:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('products', '0015_orderdetails_reward_points'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lenderreviews',
            name='about_renter',
        ),
        migrations.RemoveField(
            model_name='lenderreviews',
            name='renter',
        ),
        migrations.RemoveField(
            model_name='lenderreviews',
            name='renterRating',
        ),
        migrations.AddField(
            model_name='lenderreviews',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='requestinbox',
            name='reward_points',
            field=models.CharField(blank=True, default=0.0, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='orderdetails',
            name='reward_points',
            field=models.CharField(blank=True, default=0.0, max_length=100, null=True),
        ),
    ]
