# gui/main_window.py
"""
Interface Gráfica Principal do Sistema de Cinema (Qt Version)
"""
import sys
import os
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QGridLayout, QMessageBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import APP_NAME, APP_VERSION
from modules.relatorios import Relatorios
from database.connection import DatabaseConnection
from gui.sales_view import SalesView
from gui.inventory_view import InventoryView
from gui.movies_view import MoviesView
from gui.reports_view import ReportsView
from gui.history_view import HistoryView

STYLE_SHEET = """
QMainWindow {
    background-color: #000000;
}
QFrame#SideBar {
    background-color: #0a0a0a;
    border-right: 1px solid #1a1a1a;
}
QLabel#AppBrand {
    color: #ffffff;
    font-size: 26px;
    font-weight: 900;
    padding: 35px 15px;
}
QPushButton.NavBtn {
    background-color: transparent;
    color: #4b5563;
    text-align: left;
    padding: 12px 25px;
    margin: 4px 12px;
    font-size: 14px;
    font-weight: 700;
    border: none;
    border-radius: 10px;
}
QPushButton.NavBtn:hover {
    background-color: #111827;
    color: #0ea5e9;
}
QPushButton.NavBtn[active="true"] {
    background-color: #111827;
    color: #0ea5e9;
    border-left: 4px solid #0ea5e9;
}
QPushButton.ActionBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0ea5e9, stop:1 #2563eb);
    color: white;
    font-weight: 900;
    border-radius: 10px;
    padding: 15px 25px;
    font-size: 14px;
    border: none;
    text-transform: uppercase;
}
QPushButton.ActionBtn:hover {
    background: #38bdf8;
}
QFrame.Card {
    background-color: #0a0a0a;
    border-radius: 15px;
    border: 1px solid #1a1a1a;
}
QFrame.Card:hover {
    border: 1px solid #0ea5e9;
    background-color: #0f172a;
}
QLabel.CardTitle {
    color: #94a3b8;
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 2px;
}
QLabel.CardValue {
    color: #ffffff;
    font-size: 32px;
    font-weight: 900;
}
QLabel#HeaderTitle {
    color: #ffffff;
    font-size: 32px;
    font-weight: 900;
}
"""

class MainWindow(QMainWindow):
    """Janela Principal do Sistema usando PyQt6"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.resize(1200, 700)
        self.setStyleSheet(STYLE_SHEET)

        # Testar conexão ao iniciar
        if not DatabaseConnection.test_connection():
            QMessageBox.critical(
                self,
                "Erro de Conexão",
                "Não foi possível conectar ao banco de dados!\n"
                "Verifique as configurações em config.py"
            )
            sys.exit(1)

        self.setup_ui()

        # Atualizar dashboard a cada 30 segundos
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.atualizar_dashboard)
        self.timer.start(30000)

        # Carga inicial
        self.atualizar_dashboard()

    def setup_ui(self):
        """Monta a interface principal"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("SideBar")
        sidebar.setFixedWidth(260)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Brand
        brand = QLabel("🍿 Cine-Pena")
        brand.setObjectName("AppBrand")
        brand.setAlignment(Qt.AlignmentFlag.AlignLeft)
        sidebar_layout.addWidget(brand)
        sidebar_layout.addSpacing(20)

        # Menu Buttons
        menus = [
            ("💰 Nova Venda", self.abrir_pdv),
            ("📋 Histórico de Vendas", self.abrir_historico),
            ("📦 Gerenciar Estoque", self.abrir_estoque),
            ("🎬 Filmes e Sessões", self.abrir_filmes),
            ("📊 Relatórios", self.abrir_relatorios),
            ("⚙️ Configurações", self.em_desenvolvimento)
        ]

        for text, callback in menus:
            btn = QPushButton(text)
            btn.setProperty("class", "NavBtn")
            btn.clicked.connect(callback)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        # Exit Button
        btn_exit = QPushButton("🚪 Sair")
        btn_exit.setProperty("class", "NavBtn")
        btn_exit.clicked.connect(self.close)
        sidebar_layout.addWidget(btn_exit)
        sidebar_layout.addSpacing(20)

        # Main Content Area
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("📍 Painel de Controle")
        title.setObjectName("HeaderTitle")
        
        self.lbl_data = QLabel(datetime.now().strftime("%d/%m/%Y %H:%M"))
        self.lbl_data.setStyleSheet("color: #64748b; font-weight: bold;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.lbl_data)
        content_layout.addLayout(header_layout)

        # Cards Grid
        cards_grid = QGridLayout()
        cards_grid.setSpacing(20)

        # Criando Cards
        self.card_vendas = self.create_card("Vendas Hoje", "0", "🎟️")
        self.card_faturamento = self.create_card("Faturamento", "R$ 0,00", "💰")
        self.card_ingressos = self.create_card("Ingressos", "0", "🎫")
        self.card_ticket = self.create_card("Ticket Médio", "R$ 0,00", "📈")
        
        self.card_produtos = self.create_card("Produtos", "0", "🍿")
        self.card_liquido = self.create_card("Lucro Estimado", "R$ 0,00", "💎")
        self.card_estoque = self.create_card("Alertas Estoque", "0", "⚠️")
        self.card_impostos = self.create_card("Impostos (Dia)", "R$ 0,00", "🏦")

        cards_grid.addWidget(self.card_vendas['frame'], 0, 0)
        cards_grid.addWidget(self.card_faturamento['frame'], 0, 1)
        cards_grid.addWidget(self.card_ingressos['frame'], 0, 2)
        cards_grid.addWidget(self.card_ticket['frame'], 0, 3)
        
        cards_grid.addWidget(self.card_produtos['frame'], 1, 0)
        cards_grid.addWidget(self.card_liquido['frame'], 1, 1)
        cards_grid.addWidget(self.card_estoque['frame'], 1, 2)
        cards_grid.addWidget(self.card_impostos['frame'], 1, 3)

        content_layout.addLayout(cards_grid)

        # Ações Rápidas Toolbar
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(15)
        
        btn_venda = QPushButton("🎫 Iniciar PDV")
        btn_venda.setProperty("class", "ActionBtn")
        btn_venda.clicked.connect(self.abrir_pdv)
        
        btn_filme = QPushButton("🎬 Novo Filme")
        btn_filme.setProperty("class", "ActionBtn")
        btn_filme.clicked.connect(self.abrir_filmes)

        actions_layout.addWidget(btn_venda)
        actions_layout.addWidget(btn_filme)
        actions_layout.addStretch()

        content_layout.addLayout(actions_layout)
        content_layout.addStretch()

        # Add to Main Layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_area, 1)

    def create_card(self, title, default_value, icon="📊"):
        """Cria um widget de cartão de estatística"""
        frame = QFrame()
        frame.setProperty("class", "Card")
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(25, 25, 25, 25)
        
        header_layout = QHBoxLayout()
        lbl_title = QLabel(title)
        lbl_title.setProperty("class", "CardTitle")
        
        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet("font-size: 18px;")
        
        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        header_layout.addWidget(lbl_icon)
        
        lbl_value = QLabel(default_value)
        lbl_value.setProperty("class", "CardValue")
        
        layout.addLayout(header_layout)
        layout.addSpacing(15)
        layout.addWidget(lbl_value)
        
        return {'frame': frame, 'value_label': lbl_value}

    def atualizar_dashboard(self):
        """Atualiza os valores dos cards via banco de dados"""
        self.lbl_data.setText(datetime.now().strftime("%d/%m/%Y %H:%M"))
        
        try:
            dashboard = Relatorios.dashboard_hoje()

            # Atualizar cards com as novas labels de dict do pymysql execute_query
            v_dict = dashboard['vendas']
            self.card_vendas['value_label'].setText(str(v_dict['total_vendas'] or 0))
            self.card_faturamento['value_label'].setText(f"R$ {float(v_dict['faturamento'] or 0):.2f}")
            self.card_ingressos['value_label'].setText(str(dashboard['ingressos']['total_ingressos'] or 0))
            self.card_ticket['value_label'].setText(f"R$ {float(v_dict['ticket_medio'] or 0):.2f}")
            self.card_produtos['value_label'].setText(str(dashboard['produtos']['total_produtos'] or 0))
            self.card_liquido['value_label'].setText(f"R$ {float(v_dict['liquido'] or 0):.2f}")
            self.card_estoque['value_label'].setText(str(dashboard['alertas_estoque']['produtos_criticos'] or 0))

            faturamento = float(v_dict['faturamento'] or 0)
            liquido = float(v_dict['liquido'] or 0)
            impostos = faturamento - liquido
            self.card_impostos['value_label'].setText(f"R$ {impostos:.2f}")

        except Exception as e:
            print(f"Erro ao atualizar dashboard: {e}")

    def abrir_pdv(self):
        """Abre o módulo de Ponto de Venda"""
        dialog = SalesView(self)
        dialog.exec()
        # Após o fechamento do PDV, atualizamos o dashboard
        self.atualizar_dashboard()

    def abrir_estoque(self):
        """Abre o módulo de Gestão de Estoque"""
        dialog = InventoryView(self)
        dialog.exec()
        self.atualizar_dashboard()

    def abrir_filmes(self):
        """Abre o módulo de Gestão de Filmes e Sessões"""
        dialog = MoviesView(self)
        dialog.exec()
        self.atualizar_dashboard()

    def abrir_relatorios(self):
        """Abre o Dashboard Financeiro"""
        dialog = ReportsView(self)
        dialog.exec()

    def abrir_historico(self):
        """Abre o painel de Histórico de Vendas"""
        dialog = HistoryView(self)
        dialog.exec()

    def em_desenvolvimento(self):
        QMessageBox.information(
            self,
            "Em desenvolvimento",
            "Módulo em desenvolvimento!"
        )

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()