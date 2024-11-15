# Generated by Django 5.0.7 on 2024-11-07 22:19

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Materia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Matéria',
                'verbose_name_plural': 'Matérias',
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='Assunto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('materia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assuntos', to='quiz.materia')),
            ],
            options={
                'verbose_name': 'Assunto',
                'verbose_name_plural': 'Assuntos',
                'ordering': ['materia__nome', 'nome'],
                'unique_together': {('nome', 'materia')},
            },
        ),
        migrations.CreateModel(
            name='Questao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enunciado', models.TextField()),
                ('alternativa_a', models.CharField(max_length=500)),
                ('alternativa_b', models.CharField(max_length=500)),
                ('alternativa_c', models.CharField(max_length=500)),
                ('alternativa_d', models.CharField(max_length=500)),
                ('alternativa_e', models.CharField(blank=True, max_length=500, null=True)),
                ('alternativa_correta', models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')], max_length=1)),
                ('dificuldade', models.IntegerField(choices=[(1, 'Fácil'), (2, 'Médio'), (3, 'Difícil')], validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(3)])),
                ('explicacao', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assunto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questoes', to='quiz.assunto')),
                ('materia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questoes', to='quiz.materia')),
            ],
            options={
                'verbose_name': 'Questão',
                'verbose_name_plural': 'Questões',
                'ordering': ['materia__nome', 'assunto__nome', 'id'],
            },
        ),
        migrations.CreateModel(
            name='RespostaUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resposta_usuario', models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')], max_length=1)),
                ('data_resposta', models.DateTimeField(auto_now_add=True)),
                ('correta', models.BooleanField()),
                ('questao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='respostas', to='quiz.questao')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='respostas', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Resposta do Usuário',
                'verbose_name_plural': 'Respostas dos Usuários',
                'ordering': ['-data_resposta'],
                'unique_together': {('usuario', 'questao')},
            },
        ),
    ]
