# Generated by Django 5.0.7 on 2024-11-09 03:00

import ckeditor_uploader.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0004_questao_url_imagem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questao',
            name='enunciado',
            field=ckeditor_uploader.fields.RichTextUploadingField(),
        ),
    ]
