from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Materia, Assunto, Questao, RespostaUsuario, UserAchievement, AchievementType
from django.utils.html import format_html
from django.utils.safestring import mark_safe


CustomUser = get_user_model()

class CustomAdminMixin:
    class Media:
        css = {
            'all': [
                'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css',
            ]
        }

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    search_fields = ['email']  # ou qualquer campo que você queira para pesquisa

@admin.register(Materia)
class MateriaAdmin(CustomAdminMixin, admin.ModelAdmin):
    list_display = ('nome', 'get_total_questoes')
    search_fields = ('nome',)
    
    def get_total_questoes(self, obj):
        total = Questao.objects.filter(materia=obj).count()
        return format_html('<span class="badge bg-info">{}</span>', total)
    get_total_questoes.short_description = 'Total de Questões'

@admin.register(Assunto)
class AssuntoAdmin(CustomAdminMixin, admin.ModelAdmin):
    list_display = ('nome', 'materia', 'get_total_questoes')
    list_filter = ('materia',)
    search_fields = ('nome', 'materia__nome')
    autocomplete_fields = ['materia']
    
    def get_total_questoes(self, obj):
        total = Questao.objects.filter(assunto=obj).count()
        return format_html('<span class="badge bg-info">{}</span>', total)
    get_total_questoes.short_description = 'Total de Questões'

@admin.register(Questao)
class QuestaoAdmin(CustomAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'materia', 'assunto', 'dificuldade', 'get_preview', 'get_respostas')
    list_filter = ('materia', 'assunto', 'dificuldade', 'data_criacao')
    search_fields = ('enunciado', 'materia__nome', 'assunto__nome')
    autocomplete_fields = ['materia', 'assunto']
    readonly_fields = ('data_criacao', 'preview_questao')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': (('materia', 'assunto'), 'dificuldade', 'data_criacao')
        }),
        ('Conteúdo da Questão', {
            'fields': ('enunciado', 'preview_questao'),
            'description': 'Use o editor abaixo para criar o enunciado da questão. Você pode inserir imagens e fórmulas matemáticas.'
        }),
        ('Alternativas', {
            'fields': (
                'alternativa_a',
                'alternativa_b',
                'alternativa_c',
                'alternativa_d',
                'alternativa_e',
                'alternativa_correta'
            ),
            'description': 'Digite as alternativas e selecione a correta.'
        }),
        ('Explicação', {
            'fields': ('explicacao',),
            'description': 'Forneça uma explicação detalhada da resposta correta.'
        }),
    )
    
    def preview_questao(self, obj):
        if obj.id:
            return format_html(
                '<div class="preview-container" style="padding: 15px; border: 1px solid #ddd; '
                'border-radius: 4px; margin-top: 10px;">{}</div>',
                obj.enunciado
            )
        return "O preview estará disponível após salvar a questão."
    preview_questao.short_description = "Preview da Questão"

    def get_preview(self, obj):
        return format_html(
            '<button type="button" class="preview-btn" '
            'onclick="window.open(\'{}\', \'_blank\')" '
            'style="border: none; background: none; color: #447e9b; cursor: pointer;">'
            '<i class="fas fa-eye"></i></button>',
            reverse('admin:quiz_questao_change', args=[obj.pk])
        )
    get_preview.short_description = 'Preview'

    def get_respostas(self, obj):
        total_respostas = obj.respostas.count()
        respostas_corretas = obj.respostas.filter(correta=True).count()
        if total_respostas > 0:
            percentual = (respostas_corretas / total_respostas) * 100
            percentual_str = f"{percentual:.1f}"  # String formatada com o percentual
            cor = '#28a745' if percentual >= 70 else '#dc3545'
            return mark_safe(
                f'<span title="{respostas_corretas} corretas de {total_respostas}" style="color: {cor};">'
                f'{percentual_str}% ({respostas_corretas}/{total_respostas})</span>'
            )
        return mark_safe('<span class="text-muted">Sem respostas</span>')
    get_respostas.short_description = 'Taxa de Acerto'

    class Media:
        js = [
            'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-AMS_HTML',
        ]

        # Inline CSS/JS
        css = {
            'all': [
                'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css',
            ]
        }

@admin.register(RespostaUsuario)
class RespostaUsuarioAdmin(CustomAdminMixin, admin.ModelAdmin):
    list_display = ('usuario', 'questao', 'resposta_usuario', 'get_status', 'data_resposta')
    list_filter = ('correta', 'data_resposta', 'questao__materia', 'questao__assunto')
    search_fields = ('usuario__email', 'questao__enunciado')
    readonly_fields = ('correta', 'data_resposta')
    autocomplete_fields = ['usuario', 'questao']
    
    def get_status(self, obj):
        return format_html(
            '<span class="badge {}">{}</span>',
            'bg-success' if obj.correta else 'bg-danger',
            'Correta' if obj.correta else 'Incorreta'
        )
    get_status.short_description = 'Status'

    def has_add_permission(self, request):
        return False  # Impede a criação manual de respostas

@admin.register(AchievementType)
class AchievementTypeAdmin(CustomAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'description', 'requirement_type', 'requirement_value', 'get_icon')
    list_filter = ('requirement_type',)
    search_fields = ('name', 'description')
    
    def get_icon(self, obj):
        return format_html('<i class="{}"></i> {}', obj.icon, obj.icon)
    get_icon.short_description = 'Ícone'

@admin.register(UserAchievement)
class UserAchievementAdmin(CustomAdminMixin, admin.ModelAdmin):
    list_display = ('user', 'achievement_type', 'earned_date', 'is_completed')
    list_filter = ('is_completed', 'earned_date', 'achievement_type')
    search_fields = ('user__email', 'achievement_type__name')
    autocomplete_fields = ['user', 'achievement_type']

# Customização global do Admin
admin.site.site_header = 'Administração do Sistema de Quiz'
admin.site.site_title = 'Quiz Admin'
admin.site.index_title = 'Gerenciamento de Questões e Conquistas'


