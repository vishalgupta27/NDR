# Generated by Django 4.1.3 on 2023-07-10 06:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_alter_extendtransaction_extendstatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='extendtransaction',
            name='extendPaymentId',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]