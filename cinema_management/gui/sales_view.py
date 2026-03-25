import sys
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QComboBox, QMessageBox, QFrame, QGridLayout, QSplitter
)
from PyQt6.QtCore import Qt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from controllers.sales_ctrl import SalesController
from config import FORMAS_PAGAMENTO, TIPOS_INGRESSO

STYLE_SHEET_PDV = """
QDialog {
    background-color: #f8fafc;
}
QTableWidget {
    background-color: white;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    selection-background-color: #3b82f6;
}
QHeaderView::section {
    background-color: #f1f5f9;
    border: none;
    border-bottom: 2px solid #cbd5e1;
    padding: 6px;
    font-weight: bold;
}
QFrame.CartPanel {
    background-color: white;
    border-left: 2px solid #cbd5e1;
}
QLabel#TotalLabel {
    font-size: 28px;
    font-weight: bold;
    color: #16a34a;
}
QPushButton.AddBtn {
    background-color: #3b82f6;
    color: white;
    font-weight: bold;
    padding: 8px;
    border-radius: 4px;
}
QPushButton.AddBtn:hover { background-color: #2563eb; }
QPushButton.FinishBtn {
    background-color: #16a34a;
    color: white;
    font-weight: bold;
    font-size: 16px;
    padding: 15px;
    border-radius: 6px;
}
QPushButton.FinishBtn:hover { background-color: #15803d; }
"""

class SalesView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ponto de Venda (PDV) - CineManager")
        self.resize(1000, 700)
        self.setStyleSheet(STYLE_SHEET_PDV)
        
        self.cart_ingressos = []
        self.cart_produtos = []
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # --- LEFT PANEL (Catalog) ---
        catalog_widget = QWidget()
        catalog_layout = QVBoxLayout(catalog_widget)
        catalog_layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_sessoes = QLabel("Sessões Disponíveis")
        lbl_sessoes.setStyleSheet("font-size: 16px; font-weight: bold;")
        catalog_layout.addWidget(lbl_sessoes)
        
        self.tbl_sessoes = QTableWidget(0, 5)
        self.tbl_sessoes.setHorizontalHeaderLabels(["Filme", "Sala", "Horário", "Preço", "Ação"])
        self.tbl_sessoes.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tbl_sessoes.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        catalog_layout.addWidget(self.tbl_sessoes)
        
        lbl_bomboniere = QLabel("Bomboniere")
        lbl_bomboniere.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 15px;")
        catalog_layout.addWidget(lbl_bomboniere)
        
        self.tbl_produtos = QTableWidget(0, 4)
        self.tbl_produtos.setHorizontalHeaderLabels(["Produto", "Categoria", "Preço", "Ação"])
        self.tbl_produtos.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tbl_produtos.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        catalog_layout.addWidget(self.tbl_produtos)
        
        splitter.addWidget(catalog_widget)
        
        # --- RIGHT PANEL (Cart) ---
        cart_frame = QFrame()
        cart_frame.setProperty("class", "CartPanel")
        cart_frame.setMinimumWidth(300)
        cart_layout = QVBoxLayout(cart_frame)
        cart_layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_carrinho = QLabel("Carrinho de Compras")
        lbl_carrinho.setStyleSheet("font-size: 18px; font-weight: bold;")
        cart_layout.addWidget(lbl_carrinho)
        
        self.tbl_carrinho = QTableWidget(0, 3)
        self.tbl_carrinho.setHorizontalHeaderLabels(["Item", "Qtd/Tipo", "Valor"])
        self.tbl_carrinho.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tbl_carrinho.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        cart_layout.addWidget(self.tbl_carrinho)
        
        # Totals
        self.lbl_total = QLabel("Total: R$ 0,00")
        self.lbl_total.setObjectName("TotalLabel")
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignRight)
        cart_layout.addWidget(self.lbl_total)
        
        # Payment 
        payment_layout = QHBoxLayout()
        payment_layout.addWidget(QLabel("Forma de Pagto:"))
        self.combo_pagamento = QComboBox()
        self.combo_pagamento.addItems(FORMAS_PAGAMENTO)
        payment_layout.addWidget(self.combo_pagamento)
        cart_layout.addLayout(payment_layout)
        
        # Clear / Finish
        btn_layout = QHBoxLayout()
        btn_clear = QPushButton("Limpar Carrinho")
        btn_clear.clicked.connect(self.clear_cart)
        btn_layout.addWidget(btn_clear)
        
        btn_finish = QPushButton("Finalizar Venda")
        btn_finish.setProperty("class", "FinishBtn")
        btn_finish.clicked.connect(self.finalize_sale)
        btn_layout.addWidget(btn_finish)
        
        cart_layout.addLayout(btn_layout)
        
        splitter.addWidget(cart_frame)
        splitter.setSizes([650, 350])
        
    def load_data(self):
        """Carrega dados das tabelas via Controller"""
        # Sessoes
        sessoes = SalesController.get_upcoming_sessions()
        self.tbl_sessoes.setRowCount(0)
        for s in sessoes:
            row = self.tbl_sessoes.rowCount()
            self.tbl_sessoes.insertRow(row)
            self.tbl_sessoes.setItem(row, 0, QTableWidgetItem(s['filme']))
            self.tbl_sessoes.setItem(row, 1, QTableWidgetItem(s['sala']))
            self.tbl_sessoes.setItem(row, 2, QTableWidgetItem(s['horario']))
            self.tbl_sessoes.setItem(row, 3, QTableWidgetItem(f"R$ {s['preco']:.2f}"))
            
            btn_add = QPushButton("Adicionar")
            btn_add.setProperty("class", "AddBtn")
            # Connect explicitly taking a local capture
            btn_add.clicked.connect(lambda checked, session=s: self.add_session_to_cart(session))
            self.tbl_sessoes.setCellWidget(row, 4, btn_add)
            
        # Produtos
        produtos = SalesController.get_products()
        self.tbl_produtos.setRowCount(0)
        for p in produtos:
            row = self.tbl_produtos.rowCount()
            self.tbl_produtos.insertRow(row)
            self.tbl_produtos.setItem(row, 0, QTableWidgetItem(p['nome']))
            self.tbl_produtos.setItem(row, 1, QTableWidgetItem(p['categoria']))
            self.tbl_produtos.setItem(row, 2, QTableWidgetItem(f"R$ {p['preco']:.2f}"))
            
            btn_add = QPushButton("Adicionar")
            btn_add.setProperty("class", "AddBtn")
            btn_add.clicked.connect(lambda checked, product=p: self.add_product_to_cart(product))
            self.tbl_produtos.setCellWidget(row, 3, btn_add)

    def add_session_to_cart(self, session):
        # Aqui, na vida real seria aberto uma tela de escolher o tipo Ingress/Meia e a Cadeira
        # Por simplicidade, vamos simular que estamos adicionando INTEIRA sem cadeira
        item = {
            'sessao_id': session['id'],
            'nome': f"Ing. {session['filme']} ({session['horario']})",
            'preco_base': session['preco'],
            'tipo': 'INTEIRA' # Pode ser adaptado num dialog
        }
        self.cart_ingressos.append(item)
        self.update_cart()

    def add_product_to_cart(self, product):
        # Verifica se já está no carrinho
        for item in self.cart_produtos:
            if item['id'] == product['id']:
                item['quantidade'] += 1
                self.update_cart()
                return
                
        item = {
            'id': product['id'],
            'nome': product['nome'],
            'preco': product['preco'],
            'quantidade': 1
        }
        self.cart_produtos.append(item)
        self.update_cart()
        
    def update_cart(self):
        self.tbl_carrinho.setRowCount(0)
        
        for ing in self.cart_ingressos:
            row = self.tbl_carrinho.rowCount()
            self.tbl_carrinho.insertRow(row)
            self.tbl_carrinho.setItem(row, 0, QTableWidgetItem(ing['nome']))
            self.tbl_carrinho.setItem(row, 1, QTableWidgetItem(ing['tipo']))
            self.tbl_carrinho.setItem(row, 2, QTableWidgetItem(f"R$ {ing['preco_base']:.2f}"))
            
        for prod in self.cart_produtos:
            row = self.tbl_carrinho.rowCount()
            self.tbl_carrinho.insertRow(row)
            self.tbl_carrinho.setItem(row, 0, QTableWidgetItem(prod['nome']))
            self.tbl_carrinho.setItem(row, 1, QTableWidgetItem(f"{prod['quantidade']}x"))
            self.tbl_carrinho.setItem(row, 2, QTableWidgetItem(f"R$ {float(prod['preco']) * prod['quantidade']:.2f}"))
            
        totais = SalesController.calculate_totals(self.cart_ingressos, self.cart_produtos)
        self.lbl_total.setText(f"Total: R$ {totais['subtotal']:.2f}")

    def clear_cart(self):
        self.cart_ingressos = []
        self.cart_produtos = []
        self.update_cart()

    def finalize_sale(self):
        if not self.cart_ingressos and not self.cart_produtos:
            QMessageBox.warning(self, "Aviso", "Carrinho está vazio.")
            return
            
        forma_pagamento = self.combo_pagamento.currentText()
        sucesso, msg = SalesController.process_sale(
            forma_pagamento, 
            self.cart_ingressos, 
            self.cart_produtos
        )
        
        if sucesso:
            QMessageBox.information(self, "Sucesso", f"Venda finalizada com sucesso!\nID: {msg}")
            self.clear_cart()
        else:
            QMessageBox.critical(self, "Erro", f"Erro ao finalizar venda:\n{msg}")
