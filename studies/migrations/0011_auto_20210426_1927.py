# Generated by Django 3.1.7 on 2021-04-26 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0010_estudio_success'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweet',
            name='neg_sen',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tweet',
            name='neu_sen',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tweet',
            name='pos_sen',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=100, unique=True, verbose_name='Nombre de la categoría'),
        ),
    ]
