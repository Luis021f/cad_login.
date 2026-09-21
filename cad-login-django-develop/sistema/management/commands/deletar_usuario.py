from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Deleta um usuário do banco de dados com base no e-mail fornecido.'

    def add_arguments(self, parser):
        # Define o parâmetro obrigatório --email
        parser.add_argument(
            '--email',
            type=str,
            required=True,
            help='O endereço de e-mail do usuário que deseja deletar.'
        )

    def handle(self, *args, **options):
        email = options['email']

        try:
            # Busca o usuário pelo e-mail
            usuario = User.objects.get(email=email)
            
            # Guarda o nome/email para a mensagem de sucesso antes de deletar
            identificacao = usuario.get_username()
            usuario.delete()
            
            self.stdout.write(
                self.style.SUCCESS(f'Sucesso: O usuário "{identificacao}" ({email}) foi deletado.')
            )
            
        except User.DoesNotExist:
            raise CommandError(f'Erro: Nenhum usuário encontrado com o e-mail "{email}".')
