"""
CineManager Pro - Sistema de Gerenciamento de Cinema
Ponto de entrada da aplicação
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from gui.main_window import main as run_gui
from database.connection import DatabaseConnection
from config import APP_NAME, APP_VERSION

def setup_database():
    """configura o banco de dados na primeira execução"""
    print("=" *60)
    print(f"{APP_NAME} - v{APP_VERSION}")
    print("=" *60)
    print("\n🔧 Verificando banco de dados...")

    # Verificar conexão
    if not DatabaseConnection.test_connection():
        print("\n❌ Erro: Não foi possível conectar ao MySQL!")
        print("\n📋 Verifique:")
        print("  1. O MySQL está rodando?")
        print("  2. As credenciais em config.py estão corretas?")
        print("  3. O usuário tem permissões adequadas?")
        return False

    # Criar schema se necessário via SQLAlchemy
    print("\n🗄️  Criando/atualizando estrutura do banco de dados...")
    
    if DatabaseConnection.create_database_schema():
        print("✅ Banco de dados configurado com sucesso!")
        return True
    else:
        print("❌ Erro ao configurar banco de dados!")
        return False


def main():
    """Função principal"""
    # Configurar banco de dados
    if not setup_database():
        input("\n⏎ Pressione ENTER para sair...")
        sys.exit(1)

    print("\n🚀 Iniciando interface gráfica...")
    print("=" * 60)

    # Iniciar GUI
    try:
        run_gui()
    except KeyboardInterrupt:
        print("\n\n👋 Aplicação encerrada pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        input("\n⏎ Pressione ENTER para sair...")
        sys.exit(1)


if __name__ == "__main__":
    main()

