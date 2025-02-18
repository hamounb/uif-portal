# Generated by Django 4.2 on 2025-01-28 18:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0005_remove_invoicemodel_excus_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentmodel',
            name='invoice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='client.invoicemodel', verbose_name='فاکتور'),
        ),
        migrations.AlterField(
            model_name='valetmodel',
            name='cash',
            field=models.CharField(default='0', max_length=15, verbose_name='موجودی(ریال)'),
        ),
    ]
