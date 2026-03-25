# gui/main_window.py
"""
Interface Gráfica Principal do Sistema de Cinema
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import APP_NAME, APP_VERSION
from modules.relatorios import Relatorios
from database.connection import DatabaseConnection


class MainWindow:
    """Janela Principal do Sistema"""

    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("1200x700")
        self.root.configure(bg='#2c3e50')

        # Testar conexão ao iniciar
        if not DatabaseConnection.test_connection():
            messagebox.showerror(
                "Erro de Conexão",
                "Não foi possível conectar ao banco de dados!\n"
                "Verifique as configurações em config.py"
            )
            self.root.destroy()
            return

        self.criar_menu()
        self.criar_dashboard()

        # Atualizar dashboard a cada 30 segundos
        self.atualizar_dashboard()

    def criar_menu(self):
        """Cria a barra de menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Menu Vendas
        menu_vendas = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="💰 Vendas", menu=menu_vendas)
        menu_vendas.add_command(label="Nova Venda", command=self.abrir_vendas)
        menu_vendas.add_command(label="Histórico de Vendas", command=self.abrir_historico_vendas)
        menu_vendas.add_separator()
        menu_vendas.add_command(label="Configurar Sessões", command=self.configurar_sessoes)

        # Menu Estoque
        menu_estoque = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📦 Estoque", menu=menu_estoque)
        menu_estoque.add_command(label="Gerenciar Produtos", command=self.abrir_estoque)
        menu_estoque.add_command(label="Entrada de Produtos", command=self.entrada_estoque)
        menu_estoque.add_command(label="Relatório de Estoque", command=self.relatorio_estoque)

        # Menu Filmes
        menu_filmes = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🎬 Filmes", menu=menu_filmes)
        menu_filmes.add_command(label="Cadastrar Filme", command=self.cadastrar_filme)
        menu_filmes.add_command(label="Gerenciar Filmes", command=self.gerenciar_filmes)

        # Menu Relatórios
        menu_relatorios = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📊 Relatórios", menu=menu_relatorios)
        menu_relatorios.add_command(label="Faturamento", command=self.relatorio_faturamento)
        menu_relatorios.add_command(label="Impostos", command=self.relatorio_impostos)
        menu_relatorios.add_command(label="Produtos Mais Vendidos", command=self.relatorio_produtos)
        menu_relatorios.add_command(label="Filmes Mais Assistidos", command=self.relatorio_filmes)

        # Menu Sistema
        menu_sistema = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="⚙️ Sistema", menu=menu_sistema)
        menu_sistema.add_command(label="Configurações", command=self.configuracoes)
        menu_sistema.add_separator()
        menu_sistema.add_command(label="Sair", command=self.root.quit)

    def criar_dashboard(self):
        """Cria o dashboard principal"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Título
        titulo = tk.Label(
            main_frame,
            text=f"🎬 {APP_NAME}",
            font=("Arial", 24, "bold"),
            bg='#2c3e50',
            fg='white'
        )
        titulo.pack(pady=(0, 20))

        # Frame de cards
        cards_frame = tk.Frame(main_frame, bg='#2c3e50')
        cards_frame.pack(fill=tk.BOTH, expand=True)

        # Cards de estatísticas
        self.card_vendas = self.criar_card(
            cards_frame, "💰 Vendas Hoje", "0", "#3498db", 0, 0
        )
        self.card_faturamento = self.criar_card(
            cards_frame, "💵 Faturamento", "R$ 0,00", "#2ecc71", 0, 1
        )
        self.card_ingressos = self.criar_card(
            cards_frame, "🎫 Ingressos", "0", "#e74c3c", 0, 2
        )
        self.card_ticket_medio = self.criar_card(
            cards_frame, "📊 Ticket Médio", "R$ 0,00", "#f39c12", 0, 3
        )

        # Segunda linha de cards
        self.card_produtos = self.criar_card(
            cards_frame, "🍿 Produtos", "0", "#9b59b6", 1, 0
        )
        self.card_liquido = self.criar_card(
            cards_frame, "💎 Faturamento Líquido", "R$ 0,00", "#1abc9c", 1, 1
        )
        self.card_estoque = self.criar_card(
            cards_frame, "⚠️ Alertas Estoque", "0", "#e67e22", 1, 2
        )
        self.card_impostos = self.criar_card(
            cards_frame, "🏛️ Impostos", "R$ 0,00", "#34495e", 1, 3
        )

        # Frame de ações rápidas
        acoes_frame = tk.LabelFrame(
            main_frame,
            text="Ações Rápidas",
            font=("Arial", 14, "bold"),
            bg='#34495e',
            fg='white',
            padx=20,
            pady=20
        )
        acoes_frame.pack(fill=tk.X, pady=(20, 0))

        # Botões de ação
        self.criar_botao_acao(
            acoes_frame, "🎫 Nova Venda", self.abrir_vendas, "#3498db"
        ).pack(side=tk.LEFT, padx=5)

        self.criar_botao_acao(
            acoes_frame, "📦 Gerenciar Estoque", self.abrir_estoque, "#2ecc71"
        ).pack(side=tk.LEFT, padx=5)

        self.criar_botao_acao(
            acoes_frame, "📊 Relatórios", self.relatorio_faturamento, "#f39c12"
        ).pack(side=tk.LEFT, padx=5)

        self.criar_botao_acao(
            acoes_frame, "🎬 Cadastrar Filme", self.cadastrar_filme, "#9b59b6"
        ).pack(side=tk.LEFT, padx=5)

        # Rodapé
        rodape = tk.Label(
            main_frame,
            text=f"Sistema CineManager Pro v{APP_VERSION} | {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            font=("Arial", 10),
            bg='#2c3e50',
            fg='#95a5a6'
        )
        rodape.pack(side=tk.BOTTOM, pady=(20, 0))

    def criar_card(self, parent, titulo, valor, cor, row, col):
        """Cria um card de estatística"""
        card = tk.Frame(parent, bg=cor, relief=tk.RAISED, borderwidth=2)
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')

        # Configurar grid
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)

        # Título do card
        label_titulo = tk.Label(
            card,
            text=titulo,
            font=("Arial", 12, "bold"),
            bg=cor,
            fg='white'
        )
        label_titulo.pack(pady=(20, 5))

        # Valor do card
        label_valor = tk.Label(
            card,
            text=valor,
            font=("Arial", 24, "bold"),
            bg=cor,
            fg='white'
        )
        label_valor.pack(pady=(5, 20))

        return label_valor

    def criar_botao_acao(self, parent, texto, comando, cor):
        """Cria um botão de ação rápida"""
        btn = tk.Button(
            parent,
            text=texto,
            command=comando,
            font=("Arial", 12, "bold"),
            bg=cor,
            fg='white',
            relief=tk.RAISED,
            borderwidth=3,
            padx=20,
            pady=10,
            cursor='hand2'
        )

        # Efeito hover
        btn.bind("<Enter>", lambda e: btn.config(relief=tk.SUNKEN))
        btn.bind("<Leave>", lambda e: btn.config(relief=tk.RAISED))

        return btn

    def atualizar_dashboard(self):
        """Atualiza os dados do dashboard"""
        try:
            dashboard = Relatorios.dashboard_hoje()

            # Atualizar cards
            self.card_vendas.config(
                text=str(dashboard['vendas']['total_vendas'])
            )
            self.card_faturamento.config(
                text=f"R$ {float(dashboard['vendas']['faturamento']):.2f}"
            )
            self.card_ingressos.config(
                text=str(dashboard['ingressos']['total_ingressos'] or 0)
            )
            self.card_ticket_medio.config(
                text=f"R$ {float(dashboard['vendas']['ticket_medio']):.2f}"
            )
            self.card_produtos.config(
                text=str(dashboard['produtos']['total_produtos'] or 0)
            )
            self.card_liquido.config(
                text=f"R$ {float(dashboard['vendas']['liquido']):.2f}"
            )
            self.card_estoque.config(
                text=str(dashboard['alertas_estoque']['produtos_criticos'])
            )

            # Calcular impostos do dia
            faturamento = float(dashboard['vendas']['faturamento'])
            liquido = float(dashboard['vendas']['liquido'])
            impostos = faturamento - liquido

            self.card_impostos.config(
                text=f"R$ {impostos:.2f}"
            )

        except Exception as e:
            print(f"Erro ao atualizar dashboard: {e}")

        # Agendar próxima atualização (30 segundos)
        self.root.after(30000, self.atualizar_dashboard)

    # Métodos de navegação (placeholders)
    def abrir_vendas(self):
        messagebox.showinfo("Em desenvolvimento", "Módulo de vendas em desenvolvimento!")

    def abrir_historico_vendas(self):
        messagebox.showinfo("Em desenvolvimento", "Histórico de vendas em desenvolvimento!")

    def configurar_sessoes(self):
        messagebox.showinfo("Em desenvolvimento", "Configuração de sessões em desenvolvimento!")

    def abrir_estoque(self):
        messagebox.showinfo("Em desenvolvimento", "Gerenciamento de estoque em desenvolvimento!")

    def entrada_estoque(self):
        messagebox.showinfo("Em desenvolvimento", "Entrada de estoque em desenvolvimento!")

    def relatorio_estoque(self):
        messagebox.showinfo("Em desenvolvimento", "Relatório de estoque em desenvolvimento!")

    def cadastrar_filme(self):
        messagebox.showinfo("Em desenvolvimento", "Cadastro de filme em desenvolvimento!")

    def gerenciar_filmes(self):
        messagebox.showinfo("Em desenvolvimento", "Gerenciamento de filmes em desenvolvimento!")

    def relatorio_faturamento(self):
        messagebox.showinfo("Em desenvolvimento", "Relatório de faturamento em desenvolvimento!")

    def relatorio_impostos(self):
        messagebox.showinfo("Em desenvolvimento", "Relatório de impostos em desenvolvimento!")

    def relatorio_produtos(self):
        messagebox.showinfo("Em desenvolvimento", "Relatório de produtos em desenvolvimento!")

    def relatorio_filmes(self):
        messagebox.showinfo("Em desenvolvimento", "Relatório de filmes em desenvolvimento!")

    def configuracoes(self):
        messagebox.showinfo("Em desenvolvimento", "Configurações em desenvolvimento!")


def main():
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()