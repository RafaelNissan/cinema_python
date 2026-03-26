import sys
import os
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QTabWidget, QFrame
)
from PyQt6.QtCore import Qt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.relatorios import Relatorios

STYLE_SHEET_REPORTS = """
QDialog, QWidget {
    background-color: #020617;
    color: #f8fafc;
}
QTabWidget::pane {
    background-color: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 8px;
    margin-top: -1px;
}
QTabBar::tab {
    background-color: #0f172a;
    color: #64748b;
    padding: 12px 25px;
    font-weight: 800;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 4px;
    text-transform: uppercase;
    font-size: 11px;
}
QTabBar::tab:selected {
    background-color: #1e293b;
    color: #3b82f6;
    border-bottom: 2px solid #3b82f6;
}
QLabel {
    color: #f8fafc;
}
QTableWidget {
    background-color: #0f172a;
    border: none;
    color: #f8fafc;
    gridline-color: #1e293b;
    selection-background-color: #1e293b;
    selection-color: #3b82f6;
}
QHeaderView::section {
    background-color: #1e293b;
    color: #64748b;
    border: none;
    border-bottom: 2px solid #020617;
    padding: 12px;
    font-weight: 800;
    text-transform: uppercase;
    font-size: 11px;
}
"""

class ReportsView(QDialog):
    """Módulo de Relatórios e Gestão Financeira"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Relatórios e Gestão Financeira")
        self.resize(1000, 700)
        self.setStyleSheet(STYLE_SHEET_REPORTS)
        
        # Datas de hoje até 30 dias atrás
        self.data_fim = datetime.now().date()
        self.data_inicio = self.data_fim - timedelta(days=30)
        
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        header_layout = QHBoxLayout()
        lbl_title = QLabel(f"Dashboard Financeiro (Últimos 30 Dias: {self.data_inicio.strftime('%d/%m')} até {self.data_fim.strftime('%d/%m')})")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(lbl_title)
        
        btn_refresh = QPushButton("🔄 Atualizar")
        btn_refresh.setStyleSheet("background-color: #1e293b; color: #f8fafc; padding: 10px 15px; font-weight: 800; border-radius: 8px;")
        btn_refresh.clicked.connect(self.load_data)
        header_layout.addWidget(btn_refresh, alignment=Qt.AlignmentFlag.AlignRight)
        
        main_layout.addLayout(header_layout)
        
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # --- TAB: FATURAMENTO E VENDAS ---
        tab_faturamento = QWidget()
        lay_faturamento = QVBoxLayout(tab_faturamento)
        self.tbl_fat = QTableWidget(0, 5)
        self.tbl_fat.setHorizontalHeaderLabels([
            "Data", "Qtd. Vendas", "Faturamento Bruto", "Faturamento Líquido", "Total Impostos"
        ])
        self.tbl_fat.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        lay_faturamento.addWidget(self.tbl_fat)
        self.tabs.addTab(tab_faturamento, "💵 Faturamento Diário")
        
        # --- TAB: IMPOSTOS APURADOS ---
        tab_impostos = QWidget()
        lay_impostos = QVBoxLayout(tab_impostos)
        self.tbl_impostos = QTableWidget(0, 6)
        self.tbl_impostos.setHorizontalHeaderLabels([
            "Data", "Total Vendas", "ISS Guardado", "PIS", "COFINS", "Total Arrecadado"
        ])
        self.tbl_impostos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        lay_impostos.addWidget(self.tbl_impostos)
        self.tabs.addTab(tab_impostos, "🏛️ Extrato de Impostos")
        
        # --- TAB: TOP FILMES e PRODUTOS ---
        tab_top = QWidget()
        lay_top = QHBoxLayout(tab_top)
        
        # Filmes
        frame_f = QFrame()
        lay_f = QVBoxLayout(frame_f)
        lay_f.addWidget(QLabel("🔥 Filmes Mais Em Alta"))
        self.tbl_top_f = QTableWidget(0, 4)
        self.tbl_top_f.setHorizontalHeaderLabels(["Filme", "Gênero", "Ingressos", "Receita"])
        self.tbl_top_f.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        lay_f.addWidget(self.tbl_top_f)
        
        # Produtos
        frame_p = QFrame()
        lay_p = QVBoxLayout(frame_p)
        lay_p.addWidget(QLabel("🍿 Produtos Mais Vendidos"))
        self.tbl_top_p = QTableWidget(0, 4)
        self.tbl_top_p.setHorizontalHeaderLabels(["Produto", "Categoria", "Qtd Vendida", "Receita"])
        self.tbl_top_p.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        lay_p.addWidget(self.tbl_top_p)
        
        lay_top.addWidget(frame_f)
        lay_top.addWidget(frame_p)
        self.tabs.addTab(tab_top, "🏆 Mais Vendidos")

    def load_data(self):
        self.load_faturamento()
        self.load_impostos()
        self.load_tops()

    def load_faturamento(self):
        dados = Relatorios.faturamento_mensal(self.data_fim.year, self.data_fim.month)
        self.tbl_fat.setRowCount(0)
        for d in dados:
            row = self.tbl_fat.rowCount()
            self.tbl_fat.insertRow(row)
            self.tbl_fat.setItem(row, 0, QTableWidgetItem(d['data'].strftime('%d/%m/%Y')))
            self.tbl_fat.setItem(row, 1, QTableWidgetItem(str(d['vendas'])))
            self.tbl_fat.setItem(row, 2, QTableWidgetItem(f"R$ {float(d['faturamento_bruto']):.2f}"))
            self.tbl_fat.setItem(row, 3, QTableWidgetItem(f"R$ {float(d['faturamento_liquido']):.2f}"))
            self.tbl_fat.setItem(row, 4, QTableWidgetItem(f"R$ {float(d['impostos']):.2f}"))

    def load_impostos(self):
        resultado = Relatorios.impostos_detalhado(self.data_inicio, self.data_fim)
        detalhado = resultado.get('detalhado', [])
        
        self.tbl_impostos.setRowCount(0)
        for d in detalhado:
            row = self.tbl_impostos.rowCount()
            self.tbl_impostos.insertRow(row)
            self.tbl_impostos.setItem(row, 0, QTableWidgetItem(d['data'].strftime('%d/%m/%Y')))
            self.tbl_impostos.setItem(row, 1, QTableWidgetItem(str(d['total_vendas'])))
            self.tbl_impostos.setItem(row, 2, QTableWidgetItem(f"R$ {float(d['total_iss']):.2f}"))
            self.tbl_impostos.setItem(row, 3, QTableWidgetItem(f"R$ {float(d['total_pis']):.2f}"))
            self.tbl_impostos.setItem(row, 4, QTableWidgetItem(f"R$ {float(d['total_cofins']):.2f}"))
            self.tbl_impostos.setItem(row, 5, QTableWidgetItem(f"R$ {float(d['total_impostos']):.2f}"))

    def load_tops(self):
        # Filmes
        filmes = Relatorios.filmes_mais_vendidos(self.data_inicio, self.data_fim, 10)
        self.tbl_top_f.setRowCount(0)
        for f in filmes:
            row = self.tbl_top_f.rowCount()
            self.tbl_top_f.insertRow(row)
            self.tbl_top_f.setItem(row, 0, QTableWidgetItem(f['titulo']))
            self.tbl_top_f.setItem(row, 1, QTableWidgetItem(f['genero']))
            self.tbl_top_f.setItem(row, 2, QTableWidgetItem(str(f['ingressos_vendidos'])))
            self.tbl_top_f.setItem(row, 3, QTableWidgetItem(f"R$ {float(f['receita_total']):.2f}"))
            
        # Produtos
        produtos = Relatorios.produtos_mais_vendidos(self.data_inicio, self.data_fim, 10)
        self.tbl_top_p.setRowCount(0)
        for p in produtos:
            row = self.tbl_top_p.rowCount()
            self.tbl_top_p.insertRow(row)
            self.tbl_top_p.setItem(row, 0, QTableWidgetItem(p['produto']))
            self.tbl_top_p.setItem(row, 1, QTableWidgetItem(p['categoria']))
            self.tbl_top_p.setItem(row, 2, QTableWidgetItem(str(p['quantidade_vendida'])))
            self.tbl_top_p.setItem(row, 3, QTableWidgetItem(f"R$ {float(p['receita_total']):.2f}"))
