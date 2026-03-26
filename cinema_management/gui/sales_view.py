import sys
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QComboBox, QMessageBox, QFrame, QSplitter
)
from PyQt6.QtCore import Qt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from controllers.sales_ctrl import SalesController
from config import FORMAS_PAGAMENTO, TIPOS_INGRESSO
from gui.seats_view import SeatSelectionDialog

STYLE_SHEET_PDV = """
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
    outline: none;
}
QTableWidget::item {
    padding: 15px;
}
QHeaderView::section {
    background-color: #0a0a0a;
    color: #4b5563;
    border: none;
    border-bottom: 2px solid #1a1a1a;
    padding: 15px;
    font-weight: 900;
    text-transform: uppercase;
    font-size: 11px;
    letter-spacing: 1px;
}
QTableCornerButton::section {
    background-color: #0a0a0a;
    border: none;
}
QHeaderView::section:horizontal {
    border-left: 1px solid #1a1a1a;
}
QHeaderView::section:horizontal:first {
    border-left: none;
}
QFrame.CartPanel {
    background-color: #0a0a0a;
    border-left: 1px solid #1a1a1a;
}
QLabel#TotalLabel {
    font-size: 36px;
    font-weight: 900;
    color: #10b981;
    margin: 25px 0px;
}
QPushButton {
    background-color: #111827;
    color: #ffffff;
    padding: 12px 20px;
    border-radius: 10px;
    border: 1px solid #1a1a1a;
    font-weight: 700;
}
QPushButton:hover { 
    background-color: #1a1a1a; 
    border: 1px solid #0ea5e9;
}
QPushButton.AddBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0ea5e9, stop:1 #2563eb);
    color: white;
    font-weight: 900;
    min-width: 110px;
    min-height: 38px;
    border: none;
    text-transform: uppercase;
    font-size: 8px;
    padding: 0 2px;
}
QPushButton.AddBtn:hover { background: #38bdf8; }
QPushButton.FinishBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #059669);
    color: white;
    font-weight: 900;
    font-size: 18px;
    min-width: 250px;
    height: 70px;
    border-radius: 12px;
    border: none;
    text-transform: uppercase;
}
QPushButton.FinishBtn:hover { background: #34d399; }
QComboBox {
    background-color: #0a0a0a;
    color: white;
    border: 1px solid #1a1a1a;
    padding: 10px 15px;
    border-radius: 10px;
}
QComboBox:hover {
    border: 1px solid #0ea5e9;
}
QComboBox QAbstractItemView {
    background-color: #0a0a0a;
    selection-background-color: #111827;
    color: white;
    outline: none;
}
"""

class SalesView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ponto de Venda (PDV) - CineManager")
        self.resize(1000, 700)
        self.setStyleSheet(STYLE_SHEET_PDV)
        
        self.carrinho = []
        
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
        catalog_layout.setContentsMargins(25, 25, 25, 25)
        catalog_layout.setSpacing(15)
        
        lbl_sessoes = QLabel("Sessões Disponíveis")
        lbl_sessoes.setStyleSheet("font-size: 16px; font-weight: bold;")
        catalog_layout.addWidget(lbl_sessoes)
        
        # Tipo de Ingresso Selector
        ticket_type_layout = QHBoxLayout()
        ticket_type_layout.addWidget(QLabel("💳 Selecionar Tipo:"))
        self.combo_tipo_ingresso = QComboBox()
        self.combo_tipo_ingresso.addItems(TIPOS_INGRESSO.keys())
        self.combo_tipo_ingresso.setFixedWidth(200)
        ticket_type_layout.addWidget(self.combo_tipo_ingresso)
        ticket_type_layout.addStretch()
        catalog_layout.addLayout(ticket_type_layout)
        
        self.tbl_sessoes = QTableWidget(0, 5)
        self.tbl_sessoes.verticalHeader().setVisible(False)
        self.tbl_sessoes.verticalHeader().setDefaultSectionSize(50)
        self.tbl_sessoes.setHorizontalHeaderLabels(["Filme", "Sala", "Horário", "Preço", "Ação"])
        self.tbl_sessoes.setColumnWidth(4, 140)
        self.tbl_sessoes.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.tbl_sessoes.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tbl_sessoes.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        catalog_layout.addWidget(self.tbl_sessoes)
        
        lbl_bomboniere = QLabel("Bomboniere")
        lbl_bomboniere.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 15px;")
        catalog_layout.addWidget(lbl_bomboniere)
        
        self.tbl_produtos = QTableWidget(0, 4)
        self.tbl_produtos.verticalHeader().setVisible(False)
        self.tbl_produtos.verticalHeader().setDefaultSectionSize(50)
        self.tbl_produtos.setHorizontalHeaderLabels(["Produto", "Categoria", "Preço", "Ação"])
        self.tbl_produtos.setColumnWidth(3, 140)
        self.tbl_produtos.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
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
        
        self.tbl_cart = QTableWidget(0, 4)
        self.tbl_cart.setHorizontalHeaderLabels(["", "Item", "Qtd/Tipo", "Valor"])
        self.tbl_cart.setColumnWidth(0, 30)
        self.tbl_cart.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tbl_cart.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        cart_layout.addWidget(self.tbl_cart)
        
        btn_remover_carrinho = QPushButton("🗑️ Remover Item Selecionado")
        btn_remover_carrinho.setStyleSheet("background-color: #ef4444; color: white; padding: 8px; border-radius: 4px; font-weight: bold;")
        btn_remover_carrinho.clicked.connect(self.remove_from_cart)
        cart_layout.addWidget(btn_remover_carrinho)
        
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
        # Buscar assentos da mesma sessão que já estão no carrinho
        sessao_id = session['id']
        assentos_no_carrinho = [
            item['assento_id'] for item in self.carrinho 
            if item['tipo_item'] == 'ingresso' and item['sessao_id'] == sessao_id
        ]
        
        # Abrir diálogo de assentos passando os ocupados no carrinho
        dialog = SeatSelectionDialog(
            sessao_id=sessao_id,
            filme_titulo=session['filme'],
            sala_nome=session['sala'],
            cart_seats=assentos_no_carrinho,
            parent=self
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            assento = dialog.get_selected_seat()
            if not assento:
                return

            tipo_selecionado = self.combo_tipo_ingresso.currentText()
            multiplicador = TIPOS_INGRESSO.get(tipo_selecionado, 1.0)
            
            item = {
                'tipo_item': 'ingresso',
                'sessao_id': session['id'],
                'nome': f"Ing. {session['filme']} ({session['horario']}) [{assento}]",
                'preco_base': float(session['preco']) * multiplicador,
                'tipo': tipo_selecionado,
                'assento_id': assento,
                'quantidade': 1
            }
            self.carrinho.append(item)
            self.update_cart_view()

    def add_product_to_cart(self, product):
        for item in self.carrinho:
            if item.get('tipo_item') == 'produto' and item.get('id') == product['id']:
                item['quantidade'] += 1
                self.update_cart_view()
                return
                
        item = {
            'tipo_item': 'produto',
            'id': product['id'],
            'nome': product['nome'],
            'preco_base': product['preco'],
            'quantidade': 1
        }
        self.carrinho.append(item)
        self.update_cart_view()

    def remove_from_cart(self):
        to_remove = []
        for row in range(self.tbl_cart.rowCount()):
            item = self.tbl_cart.item(row, 0)
            if item and item.checkState() == Qt.CheckState.Checked:
                to_remove.append(row)
                
        if not to_remove:
            QMessageBox.warning(self, "Aviso", "Marque pelo menos um item no checkbox para remover.")
            return
            
        # Remover iterando de trás pra frente para não bagunçar os índices
        for row in reversed(to_remove):
            self.carrinho.pop(row)
            
        self.update_cart_view()

    def update_cart_view(self):
        self.tbl_cart.setRowCount(0)
        subtotal = 0.0
        
        for idx, item in enumerate(self.carrinho):
            row = self.tbl_cart.rowCount()
            self.tbl_cart.insertRow(row)
            
            # Coluna 0: Checkbox
            chk_item = QTableWidgetItem("")
            chk_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            chk_item.setCheckState(Qt.CheckState.Unchecked)
            self.tbl_cart.setItem(row, 0, chk_item)
            
            # Coluna 1: Nome
            self.tbl_cart.setItem(row, 1, QTableWidgetItem(item['nome']))
            
            if item['tipo_item'] == 'ingresso':
                self.tbl_cart.setItem(row, 2, QTableWidgetItem(item['tipo']))
            else:
                self.tbl_cart.setItem(row, 2, QTableWidgetItem(f"{item['quantidade']}x"))
            
            valor = float(item['preco_base']) * item['quantidade']
            subtotal += valor
            self.tbl_cart.setItem(row, 3, QTableWidgetItem(f"R$ {valor:.2f}"))
            
        self.lbl_total.setText(f"Total: R$ {subtotal:.2f}")

    def clear_cart(self):
        self.carrinho = []
        self.update_cart_view()

    def finalize_sale(self):
        if not self.carrinho:
            QMessageBox.warning(self, "Aviso", "Carrinho está vazio.")
            return
            
        cart_ingressos = [i for i in self.carrinho if i['tipo_item'] == 'ingresso']
        cart_produtos = [i for i in self.carrinho if i['tipo_item'] == 'produto']
        
        for p in cart_produtos:
            p['preco'] = p['preco_base']
        
        forma_pagamento = self.combo_pagamento.currentText()
        sucesso, msg = SalesController.process_sale(
            forma_pagamento, 
            cart_ingressos, 
            cart_produtos
        )
        
        if sucesso:
            QMessageBox.information(self, "Sucesso", f"Venda finalizada com sucesso!\nID: {msg}")
            self.clear_cart()
        else:
            QMessageBox.critical(self, "Erro", f"Erro ao finalizar venda:\n{msg}")
