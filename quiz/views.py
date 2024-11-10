from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Count, Q
from .models import Questao, RespostaUsuario, Materia, Assunto, UserAchievement
import random
from django.views.decorators.http import require_GET
from django.core.exceptions import ObjectDoesNotExist
import logging
from django.db.models import Count, F, Q

@login_required
def home(request):
    materias = Materia.objects.all()
    return render(request, 'quiz/home.html', {'materias': materias})

@login_required
def selecionar_filtros(request):
    materias = Materia.objects.all()
    return render(request, 'quiz/selecionar_filtros.html', {'materias': materias})


logger = logging.getLogger(__name__)

@require_GET
def carregar_assuntos(request):
    logger.info("carregar_assuntos view called")
    materia_id = request.GET.get('materia_id')
    logger.info(f"Received materia_id: {materia_id}")
    
    if materia_id:
        try:
            assuntos = list(Assunto.objects.filter(materia_id=materia_id).values('id', 'nome'))
            logger.info(f"Found {len(assuntos)} assuntos for materia_id {materia_id}")
            return JsonResponse(assuntos, safe=False)
        except Exception as e:
            logger.error(f"Error fetching assuntos: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    else:
        logger.warning("No materia_id provided")
        return JsonResponse({'error': 'Materia ID is required'}, status=400)


@login_required
def questao_aleatoria(request):
    materia_id = request.GET.get('materia')
    assunto_id = request.GET.get('assunto')
    dificuldade = request.GET.get('dificuldade')
    
    questoes = Questao.objects.all()
    
    if materia_id:
        questoes = questoes.filter(materia_id=materia_id)
    if assunto_id:
        questoes = questoes.filter(assunto_id=assunto_id)
    if dificuldade:
        questoes = questoes.filter(dificuldade=dificuldade)
    
    # Excluir questões já respondidas pelo usuário
    respondidas = RespostaUsuario.objects.filter(usuario=request.user).values_list('questao_id', flat=True)
    questoes = questoes.exclude(id__in=respondidas)
    
    if not questoes.exists():
        return render(request, 'quiz/sem_questoes.html')
    
    questao = random.choice(questoes)
    
    letras_alternativas = {
        'A': questao.alternativa_a,
        'B': questao.alternativa_b,
        'C': questao.alternativa_c,
        'D': questao.alternativa_d,
        'E': questao.alternativa_e,
    }

    return render(request, 'quiz/quiz.html', {'questao': questao, 'letras_alternativas': letras_alternativas})

@login_required
@require_http_methods(["POST"])
def verificar_resposta(request):
    questao_id = request.POST.get('questao_id')
    resposta_usuario = request.POST.get('resposta')
    
    if not questao_id or not resposta_usuario:
        return JsonResponse({'error': 'Dados incompletos'}, status=400)
    
    questao = get_object_or_404(Questao, id=questao_id)
    
    resposta, created = RespostaUsuario.objects.get_or_create(
        usuario=request.user,
        questao=questao,
        defaults={'resposta_usuario': resposta_usuario}
    )
    
    if not created:
        return JsonResponse({'error': 'Você já respondeu esta questão'}, status=400)
    
    return JsonResponse({
        'correta': resposta.correta,
        'alternativa_correta': questao.alternativa_correta,
        'explicacao': questao.explicacao
    })


@login_required
def desempenho(request):
    user = request.user
    
    # Get performance statistics by subject
    materias_stats = Materia.objects.annotate(
        total_questoes=Count('questoes__respostas', filter=Q(questoes__respostas__usuario=user)),
        questoes_corretas=Count('questoes__respostas', 
            filter=Q(questoes__respostas__usuario=user, questoes__respostas__correta=True))
    ).annotate(
        percentual=F('questoes_corretas') * 100.0 / F('total_questoes')
    ).values('nome', 'total_questoes', 'questoes_corretas', 'percentual')

    # Get performance statistics by topic
    assuntos_stats = Assunto.objects.annotate(
        total_questoes=Count('questoes__respostas', filter=Q(questoes__respostas__usuario=user)),
        questoes_corretas=Count('questoes__respostas',
            filter=Q(questoes__respostas__usuario=user, questoes__respostas__correta=True))
    ).annotate(
        percentual=F('questoes_corretas') * 100.0 / F('total_questoes')
    ).values('nome', 'materia__nome', 'total_questoes', 'questoes_corretas', 'percentual')

    # Get response history with pagination
    historico = RespostaUsuario.objects.filter(usuario=user).select_related(
        'questao__materia', 'questao__assunto'
    ).order_by('-data_resposta')
    
    paginator = Paginator(historico, 10)
    page = request.GET.get('page')
    historico_paginado = paginator.get_page(page)

    # Get user achievements
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

# Achievement notification system
from django.contrib.messages import success

def notify_achievement(request, achievement):
    success(request, f'🏆 Nova conquista desbloqueada: {achievement.name}!')