# Generated by Django 2.2.15 on 2022-04-15 10:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lendingcore', '0014_auto_20220414_2053'),
    ]

    operations = [
        migrations.CreateModel(
            name='Embed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='Name')),
                ('desc', models.CharField(max_length=256, verbose_name='Description')),
                ('code', models.CharField(max_length=16, verbose_name='Code')),
                ('policy', jsonfield.fields.JSONField(default={'catalogs': []}, verbose_name='Metadata')),
                ('active', models.BooleanField(default=True, help_text='Enable/Disable', verbose_name='Active')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='lendingcore_embed_creator', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='lendingcore_embed_modifier', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]