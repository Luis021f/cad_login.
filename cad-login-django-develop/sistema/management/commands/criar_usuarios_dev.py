from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    #Cria usuários de teste para cada grupo no ambiente de desenvolvimento, não é executado pelo makemigrations ou migrate.
    help = 'Cria usuários de teste para cada grupo no ambiente de desenvolvimento'

    def handle(self, *args, **options):
        # Lista dos grupos existentes
        nomes_grupos = ['administradores', 'diretoria', 'gerencia_geral', 'gerencia', 'supervisao', 'atendente', 'caixa']
        senha_padrao = 'dev12345'
        first_name = ['Administrador', 'Diretoria', 'Gerência Geral', 'Gerência', 'Supervisão', 'Atendente', 'Caixa']

        for nome in nomes_grupos:
            username = f'user_{nome}'
            email = f'{nome}@dev.com'
            first_name = nome.capitalize()

            # Cria o usuário se ele não existir
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'first_name': first_name, 'email': email, 'is_staff': False, 'is_active': True}
            )

            if created:
                user.set_password(senha_padrao)
                user.save()

                # Associa o usuário ao grupo correspondente
                try:
                    grupo = Group.objects.get(name=nome)
                    user.groups.add(grupo)
                    self.stdout.write(self.style.SUCCESS(f'Usuário "{username}" criado e associado ao grupo: Email: {email}, Senha: {senha_padrao}'))
                except Group.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'Grupo "{nome}" não encontrado. Execute as migrations primeiro.'))
            else:
                self.stdout.write(self.style.NOTICE(f'Usuário "{username}" já existe: Email: {email}, Senha: {senha_padrao}'))
