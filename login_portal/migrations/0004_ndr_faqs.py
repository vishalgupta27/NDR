# Generated by Django 4.1.2 on 2022-11-30 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_portal', '0003_analytics'),
    ]

    operations = [
        migrations.CreateModel(
            name='NDR_FAQs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('questions', models.CharField(max_length=100, null=True)),
                ('answers', models.TextField(null=True)),
            ],
        ),
    ]
