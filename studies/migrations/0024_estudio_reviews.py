# Generated by Django 3.2.2 on 2021-05-09 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0023_auto_20210509_1200'),
    ]

    operations = [
        migrations.AddField(
            model_name='estudio',
            name='reviews',
            field=models.ManyToManyField(related_name='get_reviews', to='studies.Review', verbose_name='Review'),
        ),
    ]
