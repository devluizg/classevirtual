from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from ckeditor_uploader.fields import RichTextUploadingField  
from django.contrib.auth.models import User

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

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

class AchievementType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50)  # Font Awesome class or emoji
    requirement_type = models.CharField(max_length=50, choices=[
        ('total_correct', 'Total Correct Answers'),
        ('subject_correct', 'Subject Correct Answers'),
        ('topic_correct', 'Topic Correct Answers'),
        ('streak', 'Answer Streak'),
    ])
    requirement_value = models.IntegerField()  # Number required to earn achievement
    requirement_subject = models.ForeignKey('Materia', null=True, blank=True, on_delete=models.SET_NULL)
    requirement_topic = models.ForeignKey('Assunto', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

class UserAchievement(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    achievement_type = models.ForeignKey(AchievementType, on_delete=models.CASCADE)
    earned_date = models.DateTimeField(auto_now_add=True)
    progress = models.IntegerField(default=0)  # Track progress towards achievement
    is_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'achievement_type']

@receiver(post_save, sender='quiz.RespostaUsuario')
def check_achievements(sender, instance, created, **kwargs):
    if not created:
        return

    user = instance.usuario
    if instance.correta:
        # Check total correct answers achievements
        total_correct = RespostaUsuario.objects.filter(
            usuario=user, 
            correta=True
        ).count()
        
        # Check subject-specific achievements
        subject_correct = RespostaUsuario.objects.filter(
            usuario=user,
            correta=True,
            questao__materia=instance.questao.materia
        ).count()
        
        # Check topic-specific achievements
        topic_correct = RespostaUsuario.objects.filter(
            usuario=user,
            correta=True,
            questao__assunto=instance.questao.assunto
        ).count()

        # Check and update achievements
        achievements = AchievementType.objects.all()
        for achievement in achievements:
            progress = 0
            if achievement.requirement_type == 'total_correct':
                progress = total_correct
            elif achievement.requirement_type == 'subject_correct' and achievement.requirement_subject == instance.questao.materia:
                progress = subject_correct
            elif achievement.requirement_type == 'topic_correct' and achievement.requirement_topic == instance.questao.assunto:
                progress = topic_correct

            if progress >= achievement.requirement_value:
                UserAchievement.objects.update_or_create(
                    user=user,
                    achievement_type=achievement,
                    defaults={
                        'progress': progress,
                        'is_completed': True
                    }
                )
