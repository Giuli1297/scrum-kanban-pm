# Generated by Django 3.2.6 on 2021-11-16 20:02

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('projectmanager', '0007_auto_20211116_1701'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registroactividaddiairia',
            name='fecha',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 16, 20, 2, 36, 824851, tzinfo=utc)),
        ),
    ]
