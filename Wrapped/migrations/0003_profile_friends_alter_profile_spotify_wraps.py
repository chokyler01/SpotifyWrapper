# Generated by Django 5.1.1 on 2024-11-21 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Wrapped', '0002_spotifywrap_time_range_alter_spotifywrap_wrap_data_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='friends',
            field=models.ManyToManyField(blank=True, to='Wrapped.profile'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='spotify_wraps',
            field=models.ManyToManyField(blank=True, to='Wrapped.spotifywrap'),
        ),
    ]
