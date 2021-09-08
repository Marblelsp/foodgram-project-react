# Generated by Django 3.2.5 on 2021-09-01 09:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0009_auto_20210901_0906'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopingcart',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shop_carts', to='recipes.recipe'),
        ),
        migrations.AlterField(
            model_name='shopingcart',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shop_carts', to=settings.AUTH_USER_MODEL),
        ),
    ]
