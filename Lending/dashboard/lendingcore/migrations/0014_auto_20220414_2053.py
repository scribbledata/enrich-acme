# Generated by Django 2.2.15 on 2022-04-14 15:23

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('lendingcore', '0013_auto_20220412_1829'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='metadata',
            field=jsonfield.fields.JSONField(blank=True, default={}, verbose_name='Metadata'),
        ),
        migrations.AlterField(
            model_name='catalog',
            name='metadata',
            field=jsonfield.fields.JSONField(blank=True, default={}, verbose_name='Metadata'),
        ),
        migrations.AlterField(
            model_name='column',
            name='metadata',
            field=jsonfield.fields.JSONField(blank=True, default={}, verbose_name='Metadata'),
        ),
        migrations.AlterField(
            model_name='datasource',
            name='metadata',
            field=jsonfield.fields.JSONField(blank=True, default={}, verbose_name='Metadata'),
        ),
        migrations.AlterField(
            model_name='role',
            name='metadata',
            field=jsonfield.fields.JSONField(blank=True, default={}, verbose_name='Metadata'),
        ),
    ]