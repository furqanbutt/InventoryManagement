# Generated by Django 3.2.6 on 2021-11-30 23:42

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20211201_1041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='dateAdded',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 30, 23, 42, 13, 649773, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(default=None, null=True, upload_to=''),
        ),
    ]
