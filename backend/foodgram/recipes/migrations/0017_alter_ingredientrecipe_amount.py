# Generated by Django 3.2.5 on 2021-09-21 00:37

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0016_alter_ingredientrecipe_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='amount',
            field=models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1, 'Меньше 1 поставить нельзя')], verbose_name='Количество ингредиента'),
        ),
    ]
