# Generated by Django 3.2.6 on 2021-08-19 21:38

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Pokemon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('p_id', models.IntegerField(unique=True)),
                ('favourite', models.ManyToManyField(blank=True, related_name='favourites', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['p_id'],
            },
        ),
    ]
