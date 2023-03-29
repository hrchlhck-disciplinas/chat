from datetime import datetime as dt

__all__ = ['cria_mensagem']

def cria_mensagem(usuario: str, mensagem: str, net=True, encoding='utf8') -> str:
    msg = f'{dt.strftime(dt.now(), "%d/%m/%Y - %H:%M:%S")} | < {usuario} > | {mensagem}'

    if net == True:
        return msg.encode(encoding=encoding)

    return msg