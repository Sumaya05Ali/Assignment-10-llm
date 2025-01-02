# Generated by Django 5.1.4 on 2025-01-02 06:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('property_data', '0002_alter_hotel_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='PropertySummary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('property_id', models.IntegerField()),
                ('summary', models.TextField()),
            ],
            options={
                'db_table': 'property_summaries',
            },
        ),
        migrations.AlterModelOptions(
            name='hotel',
            options={'managed': False},
        ),
    ]