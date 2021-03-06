# Generated by Django 4.0 on 2022-01-10 15:46

from django.db import migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_recipetag_taggedrecipe_recipe_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='tags',
            field=taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='recipes.TaggedRecipe', to='recipes.RecipeTag', verbose_name='Tags'),
        ),
    ]
