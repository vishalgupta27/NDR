# Generated by Django 4.1.2 on 2022-10-07 11:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_id', models.CharField(max_length=500)),
                ('plans_type', models.CharField(choices=[('Silver', 'Silver'), ('Gold ', 'Gold'), ('Platinum ', 'Platinum')], max_length=100, null=True)),
                ('subscription_title', models.CharField(max_length=200, null=True)),
                ('subscription_description', models.CharField(max_length=1000, null=True)),
                ('subscription_duration', models.IntegerField(null=True)),
                ('subscription_amount', models.CharField(max_length=100, null=True)),
                ('start_date', models.CharField(blank=True, max_length=100, null=True)),
                ('end_date', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserSubscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripeid', models.CharField(max_length=255)),
                ('stripe_subscription_id', models.CharField(max_length=255)),
                ('membership', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='rewards',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, null=True)),
                ('code', models.CharField(max_length=100, null=True)),
                ('amount', models.CharField(max_length=100, null=True)),
                ('valid_from', models.CharField(max_length=100, null=True)),
                ('valid_to', models.CharField(max_length=100, null=True)),
                ('reward_status', models.CharField(max_length=100, null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]