# Configuração do Sistema de Gerenciamento de Cinema
from tkinter.constants import CURRENT

# configuração do banco de dados mysql
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'cinema_db',
    'port': 3306,
    'charset': 'utf8mb4',
    'autocommit': False
}

# configuração do importo no Brasil
IMPOSTOS = {
    'ISS': 0.05, # 5% imposto sobre serviço
    'PIS': 0.0065, # 0.65%
    'CONFINS': 0.03 # 3%
}

# tipos de ingresso

TIPOS_INGRESSO = {
    'INTEIRA': 1.0,
    'MEIA': 0.5,
    'CORTESIA': 0.0
}

# forma de pagamento

FORMAS_PAGAMENTO = [
    'DINHEIRO',
    'DEBITO',
    'CREDITO',
    'PIX'
]

# configuração gerais

APP_NAME = "CineManeger PRO"
APP_VERSION = "1.0"
CURRENCY = "R$"

# configuração de preços base
PRECO_BASE_INGRESSO = 30.00 # preço base dos ingressos inteira
PRECO_BASE_COMBO_PEQUENO = 15.00
PRECO_BASE_COMBO_MEDIO = 20.00
PRECO_BASE_COMBO_GRANDE = 25.00