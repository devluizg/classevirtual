from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from .forms import CustomUserCreationForm
import uuid
from django.contrib.auth.forms import SetPasswordForm
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()

def generate_unique_username(first_name):
    """Gera um username único baseado no primeiro nome."""
    username = first_name.lower()
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{first_name.lower()}{counter}"
        counter += 1
    return username

def register(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = generate_unique_username(form.cleaned_data['first_name'])
            user.is_active = False
            user.activation_token = uuid.uuid4()
            user.activation_token_expiry = datetime.now() + timedelta(days=2)
            user.save()
            
            # Envio do email de confirmação
            activation_link = request.build_absolute_uri(
                reverse('accounts:activate', kwargs={'token': str(user.activation_token)})
            )
            
            html_message = render_to_string('accounts/activation_email.html', {
                'user': user,
                'activation_link': activation_link,
            })
            
            send_mail(
                'Ative sua conta',
                strip_tags(html_message),
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            messages.success(
                request,
                'Cadastro realizado com sucesso! Por favor, verifique seu email para ativar sua conta.'
            )
            return redirect('accounts:login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def activate_account(request, token):
    try:
        user = User.objects.get(activation_token=token, is_active=False)
        if timezone.now() < user.activation_token_expiry:
            user.is_active = True
            user.email_verified = True
            user.save()
            
            messages.success(request, 'Sua conta foi ativada com sucesso! Agora você pode fazer login.')
            return render(request, 'accounts/activation_success.html')
        else:
            messages.error(request, 'O link de ativação expirou. Por favor, registre-se novamente.')
            return render(request, 'accounts/activation_failed.html')
    except User.DoesNotExist:
        messages.error(
            request,
            'O link de ativação é inválido ou já foi usado. Por favor, tente se registrar novamente.'
        )
        return render(request, 'accounts/activation_failed.html')


@login_required
def dashboard(request):
    return render(request, 'accounts/dashboard.html')

def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Pegando o site atual
            current_site = get_current_site(request)
            domain = current_site.domain
            protocol = 'https' if request.is_secure() else 'http'

            # Renderiza o template do e-mail
            html_message = render_to_string('accounts/password_reset_email.html', {
                'user': user,
                'domain': domain,
                'protocol': protocol,
                'uid': uid,
                'token': token,
            })

            # Envia o e-mail
            send_mail(
                'Redefinição de Senha',
                strip_tags(html_message),
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            messages.success(
                request,
                'Email enviado! Verifique sua caixa de entrada para redefinir sua senha.'
            )
            return redirect('accounts:password_reset_done')

        except User.DoesNotExist:
            messages.error(
                request,
                'Não encontramos uma conta com este email. Verifique se digitou corretamente.'
            )
    
    return render(request, 'accounts/password_reset.html')


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Sua senha foi redefinida com sucesso!')
                return redirect('accounts:password_reset_complete')
        else:
            form = SetPasswordForm(user)
        return render(request, 'accounts/password_reset_confirm.html', {'form': form, 'validlink': True})
    else:
        messages.error(request, 'O link de redefinição de senha é inválido ou expirou.')
        return render(request, 'accounts/password_reset_confirm.html', {'validlink': False})

def password_reset_done(request):
    return render(request, 'accounts/password_reset_done.html')

def password_reset_complete(request):
    return render(request, 'accounts/password_reset_complete.html')
