# Generated by Django 3.1.7 on 2021-04-23 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0006_tweet_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='estudio',
            name='lenguaje',
            field=models.CharField(choices=[('es', 'Español'), ('en', 'Inglés'), ('pt', 'Portugués')], default='es', max_length=10),
        ),
    ]
