# Generated by Django 4.1.2 on 2022-11-30 07:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_user_uuid'),
    ]

    operations = [
        migrations.CreateModel(
            name='LendersStripeAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_account_id', models.CharField(max_length=100, null=True)),
                ('stripe_access_token', models.CharField(max_length=100, null=True)),
                ('created_at', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='reward_points',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.DeleteModel(
            name='BankAccountsDetail',
        ),
        migrations.AddField(
            model_name='lendersstripeaccount',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
