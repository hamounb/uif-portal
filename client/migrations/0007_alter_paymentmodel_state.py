# Generated by Django 4.2 on 2025-01-28 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0006_paymentmodel_invoice_alter_valetmodel_cash'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentmodel',
            name='state',
            field=models.CharField(choices=[('check', 'چک بانکی'), ('cashe', 'نقدی'), ('pos', 'پوز بانکی'), ('pos', 'درگاه اینترنتی')], default='pos', max_length=50, verbose_name='وضعیت'),
        ),
    ]
