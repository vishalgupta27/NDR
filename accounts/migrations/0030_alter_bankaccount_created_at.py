# Generated by Django 4.1.3 on 2023-07-04 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0029_alter_bankaccount_account_holder_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bankaccount',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]