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

STYLE_SHEET = """
QMainWindow {
    background-color: #0f172a;
}
QFrame#SideBar {
    background-color: #1e293b;
    border-right: 1px solid #334155;
}
QLabel#AppBrand {
    color: #f8fafc;
    font-size: 20px;
    font-weight: bold;
    padding: 20px 10px;
}
QPushButton.NavBtn {
    background-color: transparent;
    color: #cbd5e1;
    text-align: left;
    padding: 15px 20px;
    font-size: 14px;
    font-weight: bold;
    border: none;
    border-left: 4px solid transparent;
    border-radius: 0px;
}
QPushButton.NavBtn:hover {
    background-color: #334155;
    color: white;
    border-left: 4px solid #3b82f6;
}
QPushButton.ActionBtn {
    background-color: #3b82f6;
    color: white;
    font-weight: bold;
    border-radius: 6px;
    padding: 10px 15px;
    font-size: 13px;
}
QPushButton.ActionBtn:hover {
    background-color: #2563eb;
}
QFrame.Card {
    background-color: #1e293b;
    border-radius: 10px;
    border: 1px solid #334155;
}
QLabel.CardTitle {
    color: #94a3b8;
    font-size: 13px;
    font-weight: bold;
    text-transform: uppercase;
}
QLabel.CardValue {
    color: #f8fafc;
    font-size: 26px;
    font-weight: bold;
}
QLabel#HeaderTitle {
    color: #f8fafc;
    font-size: 24px;
    font-weight: bold;
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
        sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Brand
        brand = QLabel(f"🎬 {APP_NAME}")
        brand.setObjectName("AppBrand")
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(brand)
        sidebar_layout.addSpacing(20)

        # Menu Buttons
        menus = [
            ("💰 Nova Venda", self.abrir_pdv),
            ("📋 Histórico de Vendas", self.em_desenvolvimento),
            ("📦 Gerenciar Estoque", self.abrir_estoque),
            ("🎬 Filmes e Sessões", self.em_desenvolvimento),
            ("📊 Relatórios", self.em_desenvolvimento),
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
        title = QLabel("Dashboard Geral")
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
        self.card_vendas = self.create_card("Vendas Hoje", "0")
        self.card_faturamento = self.create_card("Faturamento", "R$ 0,00")
        self.card_ingressos = self.create_card("Ingressos", "0")
        self.card_ticket = self.create_card("Ticket Médio", "R$ 0,00")
        
        self.card_produtos = self.create_card("Produtos", "0")
        self.card_liquido = self.create_card("Faturamento Líquido", "R$ 0,00")
        self.card_estoque = self.create_card("Alertas Estoque", "0")
        self.card_impostos = self.create_card("Impostos (Dia)", "R$ 0,00")

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
        btn_filme.clicked.connect(self.em_desenvolvimento)

        actions_layout.addWidget(btn_venda)
        actions_layout.addWidget(btn_filme)
        actions_layout.addStretch()

        content_layout.addLayout(actions_layout)
        content_layout.addStretch()

        # Add to Main Layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_area, 1)

    def create_card(self, title, default_value):
        """Cria um widget de cartão de estatística"""
        frame = QFrame()
        frame.setProperty("class", "Card")
        # Um pouco de sombra pode ser adicionado no QT
        frame.setStyleSheet("QFrame.Card { border: 1px solid #e2e8f0; }")
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_title = QLabel(title)
        lbl_title.setProperty("class", "CardTitle")
        
        lbl_value = QLabel(default_value)
        lbl_value.setProperty("class", "CardValue")
        
        layout.addWidget(lbl_title)
        layout.addSpacing(10)
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