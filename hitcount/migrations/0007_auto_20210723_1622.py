# Generated by Django 3.2.5 on 2021-07-23 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hitcount', '0006_auto_20210604_1531'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blacklistip',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='blacklistuseragent',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='hit',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='hitcount',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
