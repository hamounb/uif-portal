# Generated by Django 4.2 on 2025-05-05 10:08

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('client', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ValetModel',
            new_name='WalletModel',
        ),
        migrations.RenameField(
            model_name='invoicemodel',
            old_name='valet',
            new_name='wallet',
        ),
        migrations.RenameField(
            model_name='paymentmodel',
            old_name='valet',
            new_name='wallet',
        ),
    ]
