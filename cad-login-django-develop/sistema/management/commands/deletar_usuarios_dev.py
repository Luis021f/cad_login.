from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    # Deleta usuários de teste do ambiente de desenvolvimento
    help = 'Deleta usuários de teste do ambiente de desenvolvimento'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Deleta todos os usuários',
        )
        parser.add_argument(
            '--dev',
            action='store_true',
            help='Deleta apenas usuários dev (padrão)',
        )
        parser.add_argument(
            '--username',
            type=str,
            help='Deleta um usuário específico pelo username',
        )

    def handle(self, *args, **options):
        if options['username']:
            # Deleta um usuário específico
            try:
                user = User.objects.get(username=options['username'])
                username = user.username
                user.delete()
                self.stdout.write(self.style.SUCCESS(f'✓ Usuário "{username}" deletado com sucesso.'))
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'✗ Usuário "{options["username"]}" não encontrado.'))
        
        elif options['all']:
            # Deleta todos os usuários
            count = User.objects.count()
            User.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'✓ {count} usuário(s) deletado(s) com sucesso.'))
        
        else:
            # Deleta apenas usuários dev (padrão)
            nomes_grupos = ['administradores', 'diretoria', 'gerencia_geral', 'gerencia', 'supervisao', 'atendente', 'caixa']
            count = 0
            
            for nome in nomes_grupos:
                username = f'user_{nome}'
                try:
                    user = User.objects.get(username=username)
                    user.delete()
                    count += 1
                    self.stdout.write(self.style.SUCCESS(f'✓ Usuário "{username}" deletado.'))
                except User.DoesNotExist:
                    self.stdout.write(self.style.NOTICE(f'○ Usuário "{username}" não encontrado.'))
            
            self.stdout.write(self.style.SUCCESS(f'\n✓ Total: {count} usuário(s) de desenvolvimento deletado(s).'))
