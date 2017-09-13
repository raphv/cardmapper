# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-12 11:37
from __future__ import unicode_literals
from os.path import split, splitext
from django.db import migrations, models

def generate_magellan_id(apps, schema_editor):
    Card = apps.get_model('cardapp', 'Card')
    for card in Card.objects.all():
        if card.image:
            card.magellan_id = splitext(split(card.image.name)[-1])[0]
            card.save()
            print("Magellan ID for card '%s' is '%s'"%(card.title, card.magellan_id))

def noop(*args, **kwargs):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('cardapp', '0002_date fix'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='card',
            options={'ordering': ['title']},
        ),
        migrations.AddField(
            model_name='card',
            name='magellan_id',
            field=models.CharField(blank=True, default=None, max_length=40, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='card',
            name='public',
            field=models.BooleanField(db_index=True, default=True, help_text='Make it visible to all users. When unchecked, only you will be able to see it'),
        ),
        migrations.AlterField(
            model_name='cardmap',
            name='public',
            field=models.BooleanField(db_index=True, default=True, help_text='Make it visible to all users. When unchecked, only you will be able to see it'),
        ),
        migrations.AlterField(
            model_name='deck',
            name='public',
            field=models.BooleanField(db_index=True, default=True, help_text='Make it visible to all users. When unchecked, only you will be able to see it'),
        ),
        migrations.RunPython(
            generate_magellan_id,
            noop,
        ),
    ]
