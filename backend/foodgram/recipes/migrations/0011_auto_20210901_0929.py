# Generated by Django 3.2.5 on 2021-09-01 09:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0010_auto_20210901_0913'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredient_recipe', to='recipes.ingredient'),
        ),
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredient_recipe', to='recipes.recipe'),
        ),
    ]
