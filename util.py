from datetime import datetime as dt

__all__ = ['cria_mensagem', 'bcolors']

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def cria_mensagem(usuario: str, mensagem: str, net=True, encoding='utf8') -> str:
  
    user = bcolors.BOLD + usuario + bcolors.ENDC

    if usuario.lower() == "servidor":
        user = bcolors.BOLD + bcolors.UNDERLINE + bcolors.WARNING + usuario + bcolors.ENDC

    msg = f'{dt.strftime(dt.now(), "%d/%m/%Y - %H:%M:%S")} | < {user} > | {mensagem}'

    if net == True:
        return msg.encode(encoding=encoding)

    return msg