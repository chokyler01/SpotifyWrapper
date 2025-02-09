# Generated by Django 5.1.1 on 2024-11-25 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Wrapped", "0003_profile_friends_alter_profile_spotify_wraps"),
    ]

    operations = [
        migrations.AlterField(
            model_name="spotifywrap",
            name="time_range",
            field=models.CharField(
                blank=True,
                choices=[
                    ("short_term", "Short Term"),
                    ("medium_term", "Medium Term"),
                    ("long_term", "Long Term"),
                ],
                max_length=20,
                null=True,
            ),
        ),
    ]
