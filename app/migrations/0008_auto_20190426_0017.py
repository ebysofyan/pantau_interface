# Generated by Django 2.1.7 on 2019-04-26 00:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_auto_20190425_2337'),
    ]

    operations = [
        migrations.AddField(
            model_name='timecrawling',
            name='total',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='timecrawling',
            name='total_noldua',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='timecrawling',
            name='total_nolsatu',
            field=models.FloatField(default=0),
        ),
    ]