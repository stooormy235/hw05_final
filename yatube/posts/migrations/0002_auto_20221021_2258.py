# Generated by Django 2.2.19 on 2022-10-21 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='title',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(),
        ),
    ]