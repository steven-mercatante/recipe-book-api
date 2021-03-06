# Generated by Django 4.0 on 2022-01-09 19:49

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('recipes', '0004_recipe_recipes_rec_public__59482a_idx'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShareConfig',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('role', models.CharField(choices=[('Editor', 'Editor'), ('Viewer', 'Viewer')], default='Editor', max_length=20)),
                ('grantee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grantee', to='users.user')),
                ('granter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='granter', to='users.user')),
            ],
        ),
    ]
