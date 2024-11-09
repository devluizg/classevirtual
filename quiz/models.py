from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from ckeditor_uploader.fields import RichTextUploadingField  # Import do CKEditor

class Materia(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    
    class Meta:
        verbose_name = 'Matéria'
        verbose_name_plural = 'Matérias'
        ordering = ['nome']

    def __str__(self):
        return self.nome

class Assunto(models.Model):
    nome = models.CharField(max_length=100)
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='assuntos')
    
    class Meta:
        verbose_name = 'Assunto'
        verbose_name_plural = 'Assuntos'
        ordering = ['materia', 'nome']
        unique_together = ['nome', 'materia']

    def __str__(self):
        return f"{self.materia.nome} - {self.nome}"

class Questao(models.Model):
    data_criacao = models.DateTimeField(auto_now_add=True)
    DIFICULDADE_CHOICES = [
        (1, _('Fácil')),
        (2, _('Médio')),
        (3, _('Difícil')),
    ]
    
    ALTERNATIVA_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
    ]

    enunciado = RichTextUploadingField()  # Campo atualizado para CKEditor com suporte a upload de imagens
    alternativa_a = models.CharField(max_length=500)
    alternativa_b = models.CharField(max_length=500)
    alternativa_c = models.CharField(max_length=500)
    alternativa_d = models.CharField(max_length=500)
    alternativa_e = models.CharField(max_length=500)
    alternativa_correta = models.CharField(max_length=1, choices=ALTERNATIVA_CHOICES)
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='questoes')
    assunto = models.ForeignKey(Assunto, on_delete=models.CASCADE, related_name='questoes')
    dificuldade = models.IntegerField(choices=DIFICULDADE_CHOICES, default=1)
    explicacao = models.TextField(blank=True)
    url_imagem = models.URLField(blank=True, null=True)  # Campo adicional para URL de imagem, se necessário
    
    class Meta:
        verbose_name = 'Questão'
        verbose_name_plural = 'Questões'
        ordering = ['materia', 'assunto', '-id']

    def __str__(self):
        return f"{self.materia.nome} - {self.assunto.nome} - Questão {self.id}"

class RespostaUsuario(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='respostas')
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE, related_name='respostas')
    resposta_usuario = models.CharField(max_length=1, choices=Questao.ALTERNATIVA_CHOICES)
    data_resposta = models.DateTimeField(auto_now_add=True)
    correta = models.BooleanField(editable=False)

    class Meta:
        verbose_name = 'Resposta do Usuário'
        verbose_name_plural = 'Respostas dos Usuários'
        ordering = ['-data_resposta']
        unique_together = ['usuario', 'questao']

    def save(self, *args, **kwargs):
        self.correta = self.resposta_usuario == self.questao.alternativa_correta
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.usuario.email} - Questão {self.questao.id} - {'Correta' if self.correta else 'Incorreta'}"
