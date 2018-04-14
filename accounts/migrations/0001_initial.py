# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254, unique=True, null=True, blank=True)),
                ('birth_date', models.DateField(null=True, blank=True)),
                ('bio', models.TextField(max_length=255, null=True, blank=True)),
                ('avatar', models.ImageField(null=True, upload_to=b'avatars/', blank=True)),
                ('country', models.CharField(max_length=50, null=True, blank=True)),
                ('city', models.CharField(max_length=50, null=True, blank=True)),
                ('fav_animal', models.CharField(max_length=50, null=True, blank=True)),
                ('hobby', models.CharField(max_length=50, null=True, blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['user'],
            },
        ),
    ]
