from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
import uuid


def cadastro(request):
    """Cria uma conta inativa e envia o link para confirmação do e-mail."""
    if request.method == "POST":
        # Os nomes correspondem aos atributos name do formulário HTML.
        username = request.POST.get("usuario")
        email = request.POST.get("email")
        senha = request.POST.get("senha")
        confirmar_senha = request.POST.get("confirmar_senha")

        # Interrompe o cadastro quando a confirmação não coincide.
        if senha != confirmar_senha:
            messages.error(request, "As senhas não coincidem.")
            return render(request, "cadastro/cadastro.html")

        # Mantém uma regra mínima de tamanho antes de criar o usuário.
        if len(senha) < 8:
            messages.error(
                request, "A senha deve ter pelo menos 8 caracteres."
            )
            return render(request, "cadastro/cadastro.html")

        # O e-mail será usado no login e não pode pertencer a outra conta.
        if User.objects.filter(email=email).exists():
            messages.error(request, "Este e-mail já está cadastrado.")
            return render(request, "cadastro/cadastro.html")

        # O User padrão exige username, embora o formulário use o nome real.
        username_unico = uuid.uuid4().hex[:30]

        # A conta começa inativa até que o e-mail seja confirmado.
        user = User.objects.create_user(
            username=username_unico,
            email=email,
            password=senha,
            first_name=username,
            is_active=False,
        )

        # O ID codificado e o token assinado impedem ativações indevidas.
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Constrói a rota de ativação usando o domínio da requisição atual.
        relative_link = reverse(
            "ativar_conta", kwargs={"uidb64": uid, "token": token}
        )
        domain = get_current_site(request).domain
        activation_url = f"http://{domain}{relative_link}"

        # Envia ao usuário as instruções para concluir o cadastro.
        assunto = "Confirme seu e-mail de cadastro"
        mensagem = (
            f"Olá, {user.first_name}!\n\n"
            f"Por favor, clique no link abaixo para ativar sua conta:\n\n"
            f"{activation_url}\n\n"
            f"Se você não solicitou este cadastro, ignore este e-mail."
        )

        send_mail(assunto, mensagem, None, [user.email], fail_silently=False)

        messages.success(
            request,
            "Cadastro realizado! Enviamos um link de ativação para o seu e-mail.",
        )
        return redirect("login")

    # Em requisições GET, apenas exibe o formulário vazio.
    return render(request, "cadastro/cadastro.html")





def ativar_conta(request, uidb64, token):
    """Ativa a conta quando o link recebido por e-mail ainda é válido."""
    try:
        # Recupera o usuário a partir do ID codificado na URL.
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # O token é vinculado ao usuário e expira conforme as regras do Django.
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Sua conta foi ativada com sucesso! Você já pode fazer login.')
    else:
        messages.error(request, 'O link de ativação é inválido ou expirou.')

    # Devolve o usuário à tela de login em ambos os resultados.
    return redirect('login')