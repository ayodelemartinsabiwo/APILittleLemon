# Generated by Django 5.0.1 on 2024-03-03 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LittleMangoAPI', '0003_cart_quantity_alter_orderitem_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='quantity',
            field=models.SmallIntegerField(),
        ),
    ]
