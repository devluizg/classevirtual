from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('', lambda request: redirect('accounts:dashboard') if request.user.is_authenticated else redirect('accounts:login')),
    path('quiz/', include('quiz.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]
