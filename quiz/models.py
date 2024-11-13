from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

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

    enunciado = RichTextUploadingField()
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
    url_imagem = models.URLField(blank=True, null=True)
    
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


class AchievementType(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nome")
    description = models.TextField(verbose_name="Descrição")
    icon_url = models.CharField(
        max_length=50,
        verbose_name="Classe do Ícone",
        default="bi bi-trophy-fill",
        help_text="Classe do ícone do Bootstrap (ex: bi bi-trophy-fill, bi bi-star-fill)"
    )
    requirement_type = models.CharField(
        max_length=50,
        verbose_name="Tipo de Requisito",
        choices=[
            ('total_correct', 'Total de respostas corretas'),
            ('subject_correct', 'Respostas corretas por matéria'),
            ('topic_correct', 'Respostas corretas por tópico'),
            ('streak', 'Sequência de respostas corretas'),
        ]
    )
    requirement_value = models.IntegerField(verbose_name="Valor do Requisito")
    requirement_subject = models.ForeignKey(
        Materia, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        verbose_name="Matéria Requerida"
    )
    requirement_topic = models.ForeignKey(
        Assunto, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        verbose_name="Tópico Requerido"
    )

    class Meta:
        verbose_name = "Tipo de Conquista"
        verbose_name_plural = "Tipos de Conquistas"

    def get_icon_class(self):
        """Retorna a classe do ícone baseada no tipo de requisito se não houver um ícone personalizado"""
        if self.icon_url and self.icon_url.startswith('bi '):
            return self.icon_url
            
        # Ícones padrão baseados no tipo de requisito
        icons = {
            'total_correct': 'bi bi-check-circle-fill',
            'subject_correct': 'bi bi-book-fill',
            'topic_correct': 'bi bi-bookmark-star-fill',
            'streak': 'bi bi-lightning-fill'
        }
        return icons.get(self.requirement_type, 'bi bi-trophy-fill')

    def __str__(self):
        return self.name



class UserAchievement(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    achievement_type = models.ForeignKey(AchievementType, on_delete=models.CASCADE)
    earned_date = models.DateTimeField(auto_now_add=True)
    progress = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'achievement_type']

    def __str__(self):
        return f"{self.user.username} - {self.achievement_type.name}"

@receiver(post_save, sender=RespostaUsuario)
def check_achievements(sender, instance, created, **kwargs):
    if not created or not instance.correta:
        return

    user = instance.usuario
    total_correct = RespostaUsuario.objects.filter(usuario=user, correta=True).count()
    subject_correct = RespostaUsuario.objects.filter(
        usuario=user,
        correta=True,
        questao__materia=instance.questao.materia
    ).count()
    topic_correct = RespostaUsuario.objects.filter(
        usuario=user,
        correta=True,
        questao__assunto=instance.questao.assunto
    ).count()

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
