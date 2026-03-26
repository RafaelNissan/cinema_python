import sys
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from controllers.sales_ctrl import SalesController

STYLE_SHEET_HISTORY = """
QDialog {
    background-color: #000000;
    color: #ffffff;
}
QLabel {
    color: #ffffff;
}
QTableWidget {
    background-color: #0a0a0a;
    border: 1px solid #1a1a1a;
    border-radius: 10px;
    color: #ffffff;
    gridline-color: #1a1a1a;
    selection-background-color: #111827;
    selection-color: #0ea5e9;
}
QHeaderView::section {
    background-color: #0a0a0a;
    color: #4b5563;
    border: none;
    border-bottom: 2px solid #000000;
    padding: 15px;
    font-weight: 900;
    text-transform: uppercase;
    font-size: 11px;
    letter-spacing: 1px;
}
"""

class HistoryView(QDialog):
    """Módulo de Histórico de Vendas Avulsas de Caixa"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Histórico de Vendas (Log de Caixa)")
        self.resize(800, 500)
        self.setStyleSheet(STYLE_SHEET_HISTORY)
        
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        lbl_title = QLabel("📜 Histórico de Transações Recentes")
        lbl_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(lbl_title)
        
        self.tbl_history = QTableWidget(0, 6)
        self.tbl_history.setHorizontalHeaderLabels([
            "ID da Venda", "Data da Transação", "Forma Pagamento", "Total Bruto", "Impostos Retidos", "Receita Líquida"
        ])
        
        header = self.tbl_history.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tbl_history.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        main_layout.addWidget(self.tbl_history)

    def load_data(self):
        logs = SalesController.get_sales_history()
        self.tbl_history.setRowCount(0)
        
        for l in logs:
            row = self.tbl_history.rowCount()
            self.tbl_history.insertRow(row)
            self.tbl_history.setItem(row, 0, QTableWidgetItem(f"#{l['id']}"))
            self.tbl_history.setItem(row, 1, QTableWidgetItem(l['data']))
            self.tbl_history.setItem(row, 2, QTableWidgetItem(l['pagamento']))
            self.tbl_history.setItem(row, 3, QTableWidgetItem(f"R$ {l['bruto']:.2f}"))
            self.tbl_history.setItem(row, 4, QTableWidgetItem(f"R$ {l['impostos']:.2f}"))
            
            # Dinheiro liquido, da um destaque verde se for lucro forte
            liquido = QTableWidgetItem(f"R$ {l['liquido']:.2f}")
            liquido.setForeground(Qt.GlobalColor.green)
            self.tbl_history.setItem(row, 5, liquido)
