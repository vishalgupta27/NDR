# Generated by Django 4.1.3 on 2023-07-03 11:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0026_remove_user_stripe_account_id_bankaccount'),
    ]

    operations = [
        migrations.DeleteModel(
            name='LendersStripeAccount',
        ),
    ]
