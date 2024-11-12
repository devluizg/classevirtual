from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'quiz'

urlpatterns = [
    path('', views.home, name='home'),
    path('questao-aleatoria/', views.questao_aleatoria, name='questao_aleatoria'),
    path('selecionar-filtros/', views.selecionar_filtros, name='selecionar_filtros'),
    path('carregar-assuntos/', views.carregar_assuntos, name='carregar_assuntos'),
    path('check-new-achievements/', views.check_new_achievements, name='check_new_achievements'),
    path('questao/<int:materia_id>/', views.questao_aleatoria, name='questao_aleatoria_materia'),
    path('questao/<int:materia_id>/<int:assunto_id>/', views.questao_aleatoria, name='questao_aleatoria_assunto'),
    path('verificar-resposta/', views.verificar_resposta, name='verificar_resposta'),
    path('desempenho/', views.desempenho, name='desempenho'),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('achievements/', views.achievements, name='achievements'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
