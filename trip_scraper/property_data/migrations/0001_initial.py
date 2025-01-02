# Generated by Django 5.1.4 on 2025-01-01 05:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Hotel',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('rating', models.CharField(max_length=10)),
                ('location', models.CharField(max_length=255)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('room_type', models.CharField(max_length=255)),
                ('price', models.FloatField()),
                ('image', models.CharField(max_length=255)),
                ('city_id', models.IntegerField()),
            ],
            options={
                'db_table': 'hotels',
                'managed': False,
            },
        ),
    ]