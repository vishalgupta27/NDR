# Generated by Django 4.1.3 on 2023-05-02 06:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_attachments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachments',
            name='attachment',
            field=models.FileField(blank=True, null=True, upload_to='user/chat_attachment'),
        ),
    ]