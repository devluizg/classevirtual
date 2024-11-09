from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include

app_name = 'quiz'

urlpatterns = [
    path('', views.home, name='home'),
    path('questao/', views.questao_aleatoria, name='questao_aleatoria'),
    path('selecionar-filtros/', views.selecionar_filtros, name='selecionar_filtros'),
    path('carregar-assuntos/', views.carregar_assuntos, name='carregar_assuntos'),
    path('carregar-assuntos/', views.carregar_assuntos, name='carregar_assuntos'),
    path('questao/<int:materia_id>/', views.questao_aleatoria, name='questao_aleatoria_materia'),
    path('questao/<int:materia_id>/<int:assunto_id>/', views.questao_aleatoria, name='questao_aleatoria_assunto'),
    path('verificar-resposta/', views.verificar_resposta, name='verificar_resposta'),
    path('desempenho/', views.desempenho, name='desempenho'),
    path('ckeditor/', include('ckeditor_uploader.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



