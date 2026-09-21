# Arquivo que verifica se o usuário pertence a um grupo específico
def verificar_grupo(user, nome_do_grupo):
    return user.groups.filter(name=nome_do_grupo).exists()
