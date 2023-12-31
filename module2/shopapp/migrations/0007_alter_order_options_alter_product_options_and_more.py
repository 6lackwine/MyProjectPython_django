# Generated by Django 4.2.3 on 2023-07-24 23:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shopapp', '0006_order_products'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['delivery_address', 'user']},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['name', 'price']},
        ),
        migrations.AddField(
            model_name='product',
            name='created_by',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
    ]
