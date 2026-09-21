# Sistema de Cadastro e Login com Ativação por E-mail

Projeto desenvolvido em Django para gerenciar cadastro, ativação de conta por e-mail e login com autenticação em duas etapas (MFA) com controle de acesso por grupos.

## 📋 Visão Geral

Sistema completo de autenticação e autorização em Django que implementa:

- ✅ Cadastro de novos usuários com validação
- ✅ Confirmação de senha
- ✅ Validação de e-mail único
- ✅ Ativação de conta através de link enviado por e-mail
- ✅ Login apenas para usuários ativos
- ✅ Autenticação em duas etapas (2FA) com código enviado por e-mail
- ✅ Painel protegido com roteamento automático por grupo
- ✅ 7 grupos de acesso diferentes
- ✅ Menu personalizado por grupo
- ✅ Gerenciamento de usuários de teste para desenvolvimento

## 🏗️ Arquitetura do Projeto

```
cadastro-login/
├── app/                           # Página inicial (homepage)
├── cadastro/                       # Registro de novos usuários
├── login/                          # Autenticação e 2FA
├── painel/                         # Painéis protegidos por grupo
├── sistema/                        # Configurações globais
├── manage.py                       # Gerenciador do Django
├── requirements.txt                # Dependências Python
└── db.sqlite3                      # Banco de dados (não versionado)
```

## 📚 Detalhes dos Apps

### 1. `app` - Página Inicial
**Responsabilidade:** Exibir a homepage pública do sistema.

**Arquivo principal:** `app/views.py`
- `home()`: Renderiza a página inicial com links para cadastro e login

**Template:** `app/templates/app/index.html`

### 2. `cadastro` - Registro de Usuários

**Responsabilidade:** Gerenciar o fluxo de cadastro e ativação de contas.

**Modelo:** Usa o modelo padrão `django.contrib.auth.models.User`

**Arquivos principais:** `cadastro/views.py`

#### Views:

- **`cadastro()`** - Processa o registro de novos usuários
  - Valida se as senhas coincidem
  - Verifica tamanho mínimo de senha (8 caracteres)
  - Verifica se o e-mail já está cadastrado
  - Cria usuário com `username` gerado por UUID (único)
  - Armazena o nome informado no formulário em `User.first_name`
  - Cria conta inativa (`is_active=False`)
  - Gera token de ativação com Django's `default_token_generator`
  - Envia link de ativação por e-mail

- **`ativar_conta(uidb64, token)`** - Ativa a conta via link de e-mail
  - Decodifica o ID do usuário (base64)
  - Valida o token assinado
  - Ativa a conta se tudo estiver correto
  - Redireciona para o login

**Link de Validação:**
```
http://seu-dominio/ativar/<uidb64>/<token>/
```
O link contém:
- `uidb64`: ID do usuário codificado em base64
- `token`: Token criptografado e assinado pelo Django (válido por tempo padrão)

**Fluxo:**
1. Usuário acessa `/cadastro/`
2. Preenche formulário com nome, email e senha
3. View valida os dados
4. Cria usuário inativo
5. Gera link de ativação seguro
6. Envia e-mail com o link
7. Usuário clica no link
8. Conta é ativada
9. Redirecionado para login

**Template:** `cadastro/templates/cadastro/cadastro.html`

### 3. `login` - Autenticação e 2FA

**Responsabilidade:** Gerenciar login, autenticação em duas etapas e logout.

**Modelo:** `TwoFactorCode`
```python
class TwoFactorCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='two_factor_codes')
    code = models.CharField(max_length=6)  # 6 dígitos
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
```

**Arquivos principais:** `login/views.py`, `login/models.py`, `login/utils.py`

#### Views:

- **`login_view()`** - Primeira etapa da autenticação
  - Localiza usuário pelo e-mail
  - Autentica com a senha
  - Verifica se conta está ativa
  - Invalida códigos MFA anteriores
  - Gera novo código MFA (6 dígitos)
  - Envia código por e-mail
  - Guarda ID do usuário em `request.session['pre_2fa_user_id']`
  - Redireciona para a tela de 2FA

- **`mfa_view()`** - Segunda etapa da autenticação (2FA)
  - Recupera usuário da sessão
  - Valida código MFA fornecido
  - Verifica se código é válido e não expirou (5 minutos)
  - Marca código como usado (uso único)
  - Cria sessão autenticada
  - Redireciona para o painel

- **`logout_view()`** - Encerra a sessão
  - Invalida a sessão do usuário
  - Redireciona para homepage

- **`painel_redirect()`** - Roteamento automático por grupo
  - Verifica o grupo do usuário autenticado
  - Redireciona para o painel correto
  - Valida hierarquia: admin > diretoria > gerência geral > gerência > supervisão > atendente > caixa

#### 2FA - Autenticação em Duas Etapas

**Fluxo:**
1. Usuário acessa `/login/` e entra e-mail e senha
2. View valida credenciais
3. Gera código MFA aleatório com 6 dígitos
4. Envia código por e-mail
5. Usuário é redirecionado para `/login/mfa/`
6. Usuário insere o código
7. Sistema valida:
   - Código existe no banco
   - Código não foi usado
   - Código não expirou (5 minutos)
8. Se válido, marca como usado e cria sessão
9. Redireciona para painel

**Características de segurança:**
- Código com 6 dígitos aleatórios
- Validade de 5 minutos
- Uso único (impossível reutilizar)
- Todos os códigos anteriores são invalidados ao novo login
- Mensagens genéricas para falhas (não expõe se e-mail existe)

**Utility:** `login/utils.py`
```python
def verificar_grupo(user, nome_do_grupo):
    """Verifica se um usuário pertence a um grupo específico"""
    return user.groups.filter(name=nome_do_grupo).exists()
```

**Templates:**
- `login/templates/login/login.html` - Formulário de login
- `login/templates/login/mfa.html` - Formulário de 2FA

### 4. `painel` - Painéis Protegidos por Grupo

**Responsabilidade:** Exibir painéis personalizados para cada grupo de usuários.

**Arquivos principais:** `painel/views.py`, `painel/templatetags/auth_extras.py`

#### Views Protegidas:

- **`painel_principal()`** - Painel inicial (lista todos os usuários)
- **`view_administrador()`** - Painel exclusivo para administradores
- **`view_diretoria()`** - Painel exclusivo para diretoria
- **`view_gerencia_geral()`** - Painel exclusivo para gerência geral
- **`view_gerencia()`** - Painel exclusivo para gerência
- **`view_supervisao()`** - Painel exclusivo para supervisão
- **`view_atendente()`** - Painel exclusivo para atendentes
- **`view_caixa()`** - Painel exclusivo para caixa

Cada view:
1. Requer autenticação (`@login_required`)
2. Verifica o grupo do usuário
3. Retorna erro 403 (Forbidden) se não pertencer ao grupo
4. Renderiza template correspondente

#### Template Tags Personalizadas

**Arquivo:** `painel/templatetags/auth_extras.py`

Filtro customizado `has_group`:
```django
{% if request.user|has_group:"diretoria" %}
    <!-- Menu exclusivo da diretoria -->
{% endif %}
```

Este filtro é usado para renderizar conteúdo personalizado baseado no grupo do usuário.

#### Menu Personalizado por Grupo

**Include:** `painel/templates/includes/nav.html`

O menu é renderizado em todos os painéis usando:
```django
{% include 'includes/nav.html' %}
```

**Estrutura do menu:**

- **Menu comum (todos os usuários):**
  - Início
  - Meu Perfil

- **Menu da Diretoria:**
  - Painel Diretoria
  - Balanço Anual

- **Menu da Gerência Geral:**
  - Painel Gerência Geral

- **Menu da Gerência:**
  - Painel Gerência

- **Menu da Supervisão:**
  - Painel Supervisão

- **Menu do Atendente:**
  - Painel Atendente

- **Menu do Caixa:**
  - Painel Caixa

- **Menu Compartilhado (Atendente + Caixa):**
  - Abrir Chamado

O menu é renderizado condicionalmente usando o filtro `has_group` para verificar a pertença a grupos.

**Templates:** `painel/templates/painel/*.html`

### 5. `sistema` - Configurações Globais

**Responsabilidade:** Configurar o projeto Django, roteamento e Management Commands.

**Arquivos principais:**
- `sistema/settings.py` - Configurações do Django
- `sistema/urls.py` - Roteamento de URLs
- `sistema/asgi.py` - Configuração ASGI
- `sistema/wsgi.py` - Configuração WSGI

#### Roteamento de URLs

**Arquivo:** `sistema/urls.py`

| URL | View | Nome | Descrição |
|-----|------|------|-----------|
| `/` | `app_view.home` | `home` | Página inicial |
| `/cadastro/` | `cadastro_view.cadastro` | `cadastro` | Formulário de cadastro |
| `/ativar/<uidb64>/<token>/` | `cadastro_view.ativar_conta` | `ativar_conta` | Ativação de conta |
| `/login/` | `login_view.login_view` | `login` | Formulário de login |
| `/login/mfa/` | `login_view.mfa_view` | `mfa` | Validação 2FA |
| `/painel/` | `login_view.painel_redirect` | `painel_redirect` | Roteamento por grupo |
| `/logout/` | `login_view.logout_view` | `logout` | Logout |
| `/painel/administrador/` | `painel_views.view_administrador` | `view_administrador` | Painel Admin |
| `/painel/diretoria/` | `painel_views.view_diretoria` | `view_diretoria` | Painel Diretoria |
| `/painel/gerencia-geral/` | `painel_views.view_gerencia_geral` | `view_gerencia_geral` | Painel Gerência Geral |
| `/painel/gerencia/` | `painel_views.view_gerencia` | `view_gerencia` | Painel Gerência |
| `/painel/supervisao/` | `painel_views.view_supervisao` | `view_supervisao` | Painel Supervisão |
| `/painel/atendente/` | `painel_views.view_atendente` | `view_atendente` | Painel Atendente |
| `/painel/caixa/` | `painel_views.view_caixa` | `view_caixa` | Painel Caixa |
| `/admin/` | Django Admin | - | Administração |

#### Management Commands

**Arquivo:** `sistema/management/commands/criar_usuarios_dev.py`

Cria usuários de teste para cada grupo (desenvolvimento):
```bash
python manage.py criar_usuarios_dev
```

**Usuários criados:**
| Grupo | Username | Email | Senha |
|-------|----------|-------|-------|
| administradores | user_administradores | administradores@dev.com | dev12345 |
| diretoria | user_diretoria | diretoria@dev.com | dev12345 |
| gerencia_geral | user_gerencia_geral | gerencia_geral@dev.com | dev12345 |
| gerencia | user_gerencia | gerencia@dev.com | dev12345 |
| supervisao | user_supervisao | supervisao@dev.com | dev12345 |
| atendente | user_atendente | atendente@dev.com | dev12345 |
| caixa | user_caixa | caixa@dev.com | dev12345 |

## 🔐 Sistema de Grupos e Controle de Acesso

### Grupos Definidos

O sistema possui 7 grupos de acesso criados automaticamente pela migration:

1. **administradores** - Acesso total ao sistema
2. **diretoria** - Acesso ao painel da diretoria
3. **gerencia_geral** - Acesso ao painel de gerência geral
4. **gerencia** - Acesso ao painel de gerência
5. **supervisao** - Acesso ao painel de supervisão
6. **atendente** - Acesso ao painel de atendimento
7. **caixa** - Acesso ao painel de caixa

### Migration dos Grupos

**Arquivo:** `login/migrations/0002_auto_20260909_1129.py`

**Comando para criar as migrações:**
```bash
python manage.py makemigrations
```

**Comando para aplicar as migrações:**
```bash
python manage.py migrate
```

**O que a migration faz:**
- Cria automaticamente os 7 grupos no banco de dados
- Usa `Group.objects.get_or_create()` para evitar duplicatas
- Permite rollback (reversão) segura

**Estrutura da migration:**
```python
def criar_grupos_acesso(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    nomes_grupos = [
        'administradores',
        'diretoria',
        'gerencia_geral',
        'gerencia',
        'supervisao',
        'atendente',
        'caixa'
    ]
    for nome in nomes_grupos:
        Group.objects.get_or_create(name=nome)

class Migration(migrations.Migration):
    dependencies = [
        ('login', '0001_initial'),
        ('auth', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(criar_grupos_acesso, reverse_code=remover_grupos_acesso),
    ]
```

## 📦 Includes de Templates

Os templates usam includes para reutilizar componentes:

### `includes/nav.html`
**Localização:** `painel/templates/includes/nav.html`

**Função:** Renderizar um menu personalizado baseado no grupo do usuário

**Carregamentos necessários:**
```django
{% load auth_extras %}
```

**Uso:**
```django
{% include 'includes/nav.html' %}
```

**Conteúdo:**
- Links comuns (Início, Meu Perfil)
- Menus específicos para cada grupo usando `{% if request.user|has_group:"grupo" %}`
- Menu compartilhado para atendentes e caixas

## 🚀 Como Executar

### Pré-requisitos
- Python 3.10+
- Django 6.1
- pip

### Instalação

1. **Clone o repositório:**
```bash
git clone <repo-url>
cd cadastro-login
```

2. **Crie um ambiente virtual:**
```bash
python -m venv env
# Windows
env\Scripts\activate
# Linux/Mac
source env/bin/activate
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

4. **Execute as migrações:**
```bash
python manage.py migrate
```

5. **Crie os grupos (automático via migration):**
```bash
# Se não foi criado automaticamente:
python manage.py migrate login 0002_auto_20260909_1129
```

6. **Crie usuários de desenvolvimento (opcional):**
```bash
python manage.py criar_usuarios_dev
```

### Configuração de E-mail

Configure as seguintes variáveis no `sistema/settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'seu-servidor-smtp.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'seu-email@dominio.com'
EMAIL_HOST_PASSWORD = 'sua-senha'
DEFAULT_FROM_EMAIL = 'seu-email@dominio.com'
```

### Executar o servidor

```bash
python manage.py runserver
```

O sistema estará disponível em: `http://127.0.0.1:8000/`

## 📝 Fluxo Completo de Autenticação

```
┌─────────────────────────────────────────────────────┐
│ 1. CADASTRO                                         │
├─────────────────────────────────────────────────────┤
│ GET  /cadastro/       → Formulário vazio            │
│ POST /cadastro/       → Validar e criar usuário     │
│      └─ Email verif.  → Mensagem de sucesso         │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│ 2. ATIVAÇÃO DE CONTA                                │
├─────────────────────────────────────────────────────┤
│ Email recebe link                                   │
│ GET  /ativar/<uid>/<token>/                         │
│      └─ Ativa conta → Redireciona para login        │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│ 3. LOGIN (1ª ETAPA)                                 │
├─────────────────────────────────────────────────────┤
│ GET  /login/          → Formulário de login         │
│ POST /login/          → Validar email e senha       │
│      └─ OK            → Gera código MFA             │
│      └─ Envia email   → Armazena em sessão          │
│                       → Redireciona para 2FA        │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│ 4. 2FA (2ª ETAPA)                                   │
├─────────────────────────────────────────────────────┤
│ GET  /login/mfa/      → Formulário de código        │
│ POST /login/mfa/      → Validar código              │
│      └─ OK            → Marca como usado            │
│      └─ Cria sessão   → Redireciona para painel     │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│ 5. ROTEAMENTO DE PAINEL                             │
├─────────────────────────────────────────────────────┤
│ GET  /painel/         → painel_redirect()           │
│      └─ Verifica grupo → Redireciona para painel    │
│                         específico do grupo         │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│ 6. PAINEL PROTEGIDO                                 │
├─────────────────────────────────────────────────────┤
│ GET  /painel/<grupo>/  → View com permissão        │
│      └─ Renderiza template personalizado            │
│      └─ Inclui nav.html (menu por grupo)            │
└─────────────────────────────────────────────────────┘
```

## 📦 Dependências

Ver arquivo [requirements.txt](requirements.txt):
- Django==6.1
- asgiref==3.12.1
- sqlparse==0.5.5
- tzdata==2026.3
- requests==2.34.2
- certifi==2026.7.22
- charset-normalizer==3.5.1
- idna==3.19
- urllib3==2.7.0

## 🗄️ Banco de Dados

**Arquivo:** `db.sqlite3` (não versionado)

**Modelos principais:**
- `django.contrib.auth.models.User` - Usuários do sistema
- `django.contrib.auth.models.Group` - Grupos de acesso
- `login.models.TwoFactorCode` - Códigos 2FA temporários

## 🔍 Segurança

- ✅ CSRF protection em todos os formulários
- ✅ Hash de senha usando Django's password hasher
- ✅ Tokens de ativação criptografados e assinados
- ✅ Códigos MFA com expiração de 5 minutos
- ✅ Uso único de códigos MFA
- ✅ Mensagens de erro genéricas (não expõe dados)
- ✅ Validação de grupo em todas as views protegidas
- ✅ `login_required` em painéis
- ✅ Username gerado com UUID para evitar duplicidades

## 📝 Notas de Desenvolvimento

- O banco SQLite está no `.gitignore` e não deve ser versionado
- Senhas e configurações SMTP não devem estar no repositório
- Use variáveis de ambiente para dados sensíveis
- Os usuários de desenvolvimento são apenas para testes
- O comando `criar_usuarios_dev` não é executado automaticamente

## 📄 Documentação Completa

Para detalhes técnicos adicionais, consulte [DOCUMENTACAO.md](DOCUMENTACAO.md)

## Fluxo de cadastro e ativação

1. O usuário preenche cadastro com nome, e-mail e senha.
2. O sistema valida:
   - senha e confirmação iguais
   - senha com pelo menos 8 caracteres
   - e-mail ainda não cadastrado
3. O usuário é criado como inativo.
4. Um link de ativação é gerado e enviado por e-mail.
5. Ao clicar no link, o sistema ativa o usuário.
6. O usuário informa o e-mail e a senha na tela de login.
7. O sistema envia um código MFA de seis dígitos por e-mail.
8. O usuário informa o código na segunda etapa e acessa o painel.

## Fluxo de autenticação em duas etapas

1. O sistema localiza o usuário pelo e-mail informado.
2. A senha é validada usando o sistema de autenticação padrão do Django.
3. Códigos MFA anteriores e ainda não usados são invalidados.
4. Um novo código de seis dígitos é salvo no banco e enviado por e-mail.
5. O ID do usuário fica temporariamente armazenado na sessão.
6. O código é aceito somente se não tiver sido usado e ainda estiver dentro do prazo de 5 minutos.
7. Após a validação, o código é marcado como usado, a sessão é autenticada e o usuário é redirecionado para o painel.

## Fluxo de acesso ao painel por grupo

1. Após login bem-sucedido, o usuário é redirecionado para `/painel/`.
2. O sistema verifica a qual grupo o usuário pertence.
3. O usuário é direcionado automaticamente para o painel específico do seu perfil.
4. Tentativas de acessar painéis de outros grupos resultam em erro 403 (Forbidden).

## Desenvolvimento e Testes

### Criar usuários de teste

Execute o comando para criar um usuário para cada grupo:

```bash
python manage.py criar_usuarios_dev
```

Usuários criados:
- Username: `user_administradores` | Senha: `dev12345`
- Username: `user_diretoria` | Senha: `dev12345`
- Username: `user_gerencia_geral` | Senha: `dev12345`
- Username: `user_gerencia` | Senha: `dev12345`
- Username: `user_supervisao` | Senha: `dev12345`
- Username: `user_atendente` | Senha: `dev12345`
- Username: `user_caixa` | Senha: `dev12345`

### Remover usuários de teste

Para remover os usuários de desenvolvimento:

```bash
# Remove apenas usuários dev
python manage.py deletar_usuarios_dev

# Remove um usuário específico
python manage.py deletar_usuarios_dev --username user_administradores

# Remove todos os usuários
python manage.py deletar_usuarios_dev --all
```

## Estrutura do projeto

```text
cadastro-login/
├── app/
│   ├── templates/
│   │   └── app/
│   └── views.py
├── cadastro/
│   ├── templates/
│   │   └── cadastro/
│   └── views.py
├── login/
│   ├── templates/
│   │   └── login/
│   │       ├── login.html
│   │       └── mfa.html
│   ├── models.py           # Modelo TwoFactorCode
│   └── views.py
├── painel/
│   ├── templates/
│   │   └── painel/
│   └── views.py
├── sistema/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── db.sqlite3
├── manage.py
├── env/
├── requirements.txt
├── README.md
└── .gitignore
```

## Tecnologias

- Python
- Django 6.1
- SQLite
- HTML
- SMTP para envio de e-mails

## Pré-requisitos

- Python 3.10 ou superior
- Ambiente virtual
- Git opcional

## Como executar

1. Acesse a pasta do projeto:

```bash
cd cadastro-login
```

2. Ative o ambiente virtual:

No Windows:

```bash
env\Scripts\activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Execute as migrações:

```bash
python manage.py migrate
```

5. Inicie o servidor:

```bash
python manage.py runserver
```

6. Acesse no navegador:

```text
http://127.0.0.1:8000/
```

## Rotas principais

- `/` — página inicial
- `/cadastro/` — cadastro de usuário
- `/login/` — login
- `/painel/` — painel principal (requer autenticação)
- `/logout/` — encerra a sessão
- `/ativar/<uidb64>/<token>/` — ativação da conta
- `/admin/` — painel administrativo do Django

## Configuração de e-mail

A aplicação usa o backend SMTP do Django para enviar o link de ativação e o código MFA. O arquivo `sistema/settings.py` contém as configurações do e-mail, incluindo:

- `EMAIL_BACKEND`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_USE_TLS`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `DEFAULT_FROM_EMAIL`

Para funcionar corretamente, informe as credenciais do serviço de e-mail no arquivo de configuração antes de testar o cadastro.

O e-mail do código MFA usa atualmente o remetente `no-reply@difusao.tech`, definido em `login/views.py`. Em produção, esse remetente deve ser alinhado ao serviço SMTP configurado em `settings.py`.

Exemplo de configuração:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'seu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'sua-senha-ou-app-password'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

> Em ambiente de desenvolvimento, também é possível usar o backend de console para visualizar os e-mails no terminal, mas a implementação atual está configurada para SMTP.

## Observações importantes

- O campo `username` do Django é gerado automaticamente e não é mostrado ao usuário final.
- O nome real do usuário é salvo em `first_name`.
- A verificação de usuário duplicado é feita pelo `email`.
- Usuários que ainda não ativaram a conta não podem fazer login.
- O código MFA expira após 5 minutos e não pode ser reutilizado.
- É necessário configurar o SMTP para testar o envio do link de ativação e do código MFA.

## Criar usuário administrador

Para acessar a área administrativa do Django:

```bash
python manage.py createsuperuser
```

Depois, acesse:

```text
http://127.0.0.1:8000/admin/
```

## Licença

Este projeto foi desenvolvido para fins de estudo e prática com Django.
