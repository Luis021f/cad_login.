from django import template
from login.utils import verificar_grupo  # Importa a função que verifica usuario e grupo

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    ''' Repassa o trabalho para a função do seu utils.py para não repetir código,
     necessário para que o filtro funcione corretamente no template, pois o Django necessita de usar templatetags 
     para que o filtro seja reconhecido e utilizado nos templates.'''
    return verificar_grupo(user, group_name)
