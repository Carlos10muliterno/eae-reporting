# Generated by Django 3.2.2 on 2021-05-07 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studies', '0021_alter_estudio_fintech'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estudio',
            name='fintech',
            field=models.CharField(max_length=50, verbose_name='Nombre de la Fintech'),
        ),
    ]
