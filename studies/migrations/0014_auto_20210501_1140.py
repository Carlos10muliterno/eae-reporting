# Generated by Django 3.1.7 on 2021-05-01 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0013_estudio_graph10'),
    ]

    operations = [
        migrations.AddField(
            model_name='estudio',
            name='neg_sen',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='estudio',
            name='neu_sen',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='estudio',
            name='pos_sen',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
    ]
