# Generated by Django 3.2.23 on 2023-12-31 19:41

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_forum', '0002_remove_answer_subject'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='body',
            field=ckeditor.fields.RichTextField(),
        ),
        migrations.AlterField(
            model_name='question',
            name='body',
            field=ckeditor.fields.RichTextField(blank=True, default='', null=True),
        ),
    ]
