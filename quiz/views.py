from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_GET
from django.core.paginator import Paginator
from django.db.models import Count, F, Q
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.messages import success
from django.utils import timezone
from .models import Questao, RespostaUsuario, Materia, Assunto, UserAchievement, AchievementType
import random
import logging
from django.contrib import messages

logger = logging.getLogger(__name__)

@login_required
def home(request):
    materias = Materia.objects.all()
    return render(request, 'quiz/home.html', {'materias': materias})

@login_required
def selecionar_filtros(request):
    materias = Materia.objects.all()
    return render(request, 'quiz/selecionar_filtros.html', {'materias': materias})

@require_GET
def carregar_assuntos(request):
    materia_id = request.GET.get('materia_id')
    if materia_id:
        assuntos = list(Assunto.objects.filter(materia_id=materia_id).values('id', 'nome'))
        return JsonResponse(assuntos, safe=False)
    return JsonResponse({'error': 'Materia ID is required'}, status=400)

@login_required
def questao_aleatoria(request):
    logger.info(f"Received request with GET parameters: {request.GET}")
    
    materia_id = request.GET.get('materia')
    assunto_id = request.GET.get('assunto')
    dificuldade = request.GET.get('dificuldade')
    
    query = Questao.objects.all()
    
    if materia_id and materia_id != 'todas':
        query = query.filter(materia_id=materia_id)
        logger.info(f"Filtered by materia_id: {materia_id}")
    
    if assunto_id and assunto_id != 'todos':
        query = query.filter(assunto_id=assunto_id)
        logger.info(f"Filtered by assunto_id: {assunto_id}")
    
    if dificuldade and dificuldade != 'todas':
        query = query.filter(dificuldade=dificuldade)
        logger.info(f"Filtered by dificuldade: {dificuldade}")
    
    respondidas = RespostaUsuario.objects.filter(
        usuario=request.user
    ).values_list('questao_id', flat=True)
    
    query = query.exclude(id__in=respondidas)
    
    if not query.exists():
        logger.warning("No questions found with current filters")
        context = {
            'filtros': {
                'materia': Materia.objects.filter(id=materia_id).first() if materia_id and materia_id != 'todas' else None,
                'assunto': Assunto.objects.filter(id=assunto_id).first() if assunto_id and assunto_id != 'todos' else None,
                'dificuldade': dict(Questao.DIFICULDADE_CHOICES).get(int(dificuldade)) if dificuldade and dificuldade != 'todas' else 'Todas'
            }
        }
        return render(request, 'quiz/sem_questoes.html', context)
    
    questao = random.choice(list(query))
    
    letras_alternativas = {
        'A': questao.alternativa_a,
        'B': questao.alternativa_b,
        'C': questao.alternativa_c,
        'D': questao.alternativa_d,
        'E': questao.alternativa_e,
    }
    
    logger.info(f"Selected question ID: {questao.id}")
    
    return render(request, 'quiz/quiz.html', {
        'questao': questao,
        'letras_alternativas': letras_alternativas,
        'filtros_ativos': {
            'materia': materia_id,
            'assunto': assunto_id,
            'dificuldade': dificuldade
        }
    })

@login_required
@require_http_methods(["POST"])
def verificar_resposta(request):
    questao_id = request.POST.get('questao_id')
    resposta_usuario = request.POST.get('resposta')
    
    if not questao_id or not resposta_usuario:
        return JsonResponse({'error': 'Dados incompletos'}, status=400)
    
    questao = get_object_or_404(Questao, id=questao_id)
    
    if RespostaUsuario.objects.filter(usuario=request.user, questao=questao).exists():
        return JsonResponse({'error': 'Questão já respondida'}, status=400)
    
    correta = (resposta_usuario.upper() == questao.alternativa_correta.upper())
    resposta = RespostaUsuario.objects.create(
        usuario=request.user,
        questao=questao,
        resposta_usuario=resposta_usuario,
        correta=correta
    )
    
    # Verificar conquistas
    new_achievements = check_achievements(request.user, resposta)
    
    # Adicionar mensagens para novas conquistas
    for achievement in new_achievements:
        messages.success(request, f'🏆 Nova conquista desbloqueada: {achievement.name}!')
    
    return JsonResponse({
        'correta': correta,
        'alternativa_correta': questao.alternativa_correta,
        'explicacao': questao.explicacao,
        'new_achievements': [{'name': a.name, 'description': a.description, 'icon': a.icon} for a in new_achievements]
    })

@login_required
def desempenho(request):
    user = request.user
    
    materias_stats = Materia.objects.annotate(
        total_questoes=Count('questoes__respostas', filter=Q(questoes__respostas__usuario=user)),
        questoes_corretas=Count('questoes__respostas', 
            filter=Q(questoes__respostas__usuario=user, questoes__respostas__correta=True))
    ).annotate(
        percentual=F('questoes_corretas') * 100.0 / F('total_questoes')
    ).values('nome', 'total_questoes', 'questoes_corretas', 'percentual')

    assuntos_stats = Assunto.objects.annotate(
        total_questoes=Count('questoes__respostas', filter=Q(questoes__respostas__usuario=user)),
        questoes_corretas=Count('questoes__respostas',
            filter=Q(questoes__respostas__usuario=user, questoes__respostas__correta=True))
    ).annotate(
        percentual=F('questoes_corretas') * 100.0 / F('total_questoes')
    ).values('nome', 'materia__nome', 'total_questoes', 'questoes_corretas', 'percentual')

    historico = RespostaUsuario.objects.filter(usuario=user).select_related(
        'questao__materia', 'questao__assunto'
    ).order_by('-data_resposta')
    
    paginator = Paginator(historico, 10)
    page = request.GET.get('page')
    historico_paginado = paginator.get_page(page)

    achievements = UserAchievement.objects.filter(
        user=user, 
        is_completed=True
    ).select_related('achievement_type').order_by('-earned_date')

    context = {
        'materias_stats': materias_stats,
        'assuntos_stats': assuntos_stats,
        'historico': historico_paginado,
        'achievements': achievements,
    }
    
    return render(request, 'quiz/desempenho.html', context)

@login_required
def check_new_achievements(request):
    new_achievements = UserAchievement.objects.filter(
        user=request.user,
        earned_date__gte=timezone.now() - timezone.timedelta(minutes=5),
        is_completed=True
    ).select_related('achievement_type')
    
    return JsonResponse({
        'new_achievements': [
            {
                'name': ua.achievement_type.name,
                'description': ua.achievement_type.description,
                'icon': ua.achievement_type.icon
            }
            for ua in new_achievements
        ]
    })

def check_achievements(user, resposta):
    new_achievements = []
    if resposta.correta:
        total_correct = RespostaUsuario.objects.filter(usuario=user, correta=True).count()
        subject_correct = RespostaUsuario.objects.filter(
            usuario=user,
            correta=True,
            questao__materia=resposta.questao.materia
        ).count()
        topic_correct = RespostaUsuario.objects.filter(
            usuario=user,
            correta=True,
            questao__assunto=resposta.questao.assunto
        ).count()

        achievements = AchievementType.objects.all()
        for achievement in achievements:
            progress = 0
            if achievement.requirement_type == 'total_correct':
                progress = total_correct
            elif achievement.requirement_type == 'subject_correct' and achievement.requirement_subject == resposta.questao.materia:
                progress = subject_correct
            elif achievement.requirement_type == 'topic_correct' and achievement.requirement_topic == resposta.questao.assunto:
                progress = topic_correct

            if progress >= achievement.requirement_value:
                user_achievement, created = UserAchievement.objects.update_or_create(
                    user=user,
                    achievement_type=achievement,
                    defaults={
                        'progress': progress,
                        'is_completed': True
                    }
                )
                if created:
                    new_achievements.append(achievement)

    return new_achievements

def notify_achievement(request, achievement):
    success(request, f'🏆 Nova conquista desbloqueada: {achievement.name}!')

@login_required
def achievements(request):
    user_achievements = UserAchievement.objects.filter(user=request.user).select_related('achievement_type')
    achieved_ids = user_achievements.values_list('achievement_type_id', flat=True)
    available_achievements = AchievementType.objects.exclude(id__in=achieved_ids)
    
    context = {
        'user_achievements': user_achievements,
        'available_achievements': available_achievements,
    }
    
    return render(request, 'quiz/achievements.html', context)
