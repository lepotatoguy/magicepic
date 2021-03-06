# Generated by Django 3.2.4 on 2021-11-29 08:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0009_cartitem_variations'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='cart',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.cart'),
        ),
    ]
