# Generated by Django 4.1.2 on 2022-12-26 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_lendersstripeaccount_user_reward_points_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='notifications',
            name='screen_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
    ]
