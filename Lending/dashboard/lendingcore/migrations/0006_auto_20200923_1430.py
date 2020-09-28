# Generated by Django 2.2.1 on 2020-09-23 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lendingcore', '0005_auto_20200519_1131'),
    ]

    operations = [
        migrations.AddField(
            model_name='column',
            name='pii',
            field=models.BooleanField(default=False, help_text='Has PII (or quasi PII)', verbose_name='PII'),
        ),
        migrations.AlterField(
            model_name='column',
            name='sensitive',
            field=models.BooleanField(default=False, help_text='Has Sensitive Information', verbose_name='Sensitive'),
        ),
    ]