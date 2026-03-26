import sys
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QMessageBox, QLineEdit, QFormLayout, QComboBox
)
from PyQt6.QtCore import Qt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from controllers.inventory_ctrl import InventoryController

STYLE_SHEET_INVENTORY = """
QDialog {
    background-color: #000000;
    color: #ffffff;
}
QLabel {
    color: #ffffff;
}
QLineEdit, QComboBox {
    background-color: #0a0a0a;
    border: 1px solid #1a1a1a;
    padding: 12px;
    border-radius: 10px;
    color: #ffffff;
}
QLineEdit:focus, QComboBox:hover {
    border: 1px solid #0ea5e9;
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
}
QTableCornerButton::section {
    background-color: #0a0a0a;
    border: none;
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
QPushButton.PrimaryBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0ea5e9, stop:1 #2563eb);
    color: white;
    font-weight: 900;
    border: none;
}
QPushButton.PrimaryBtn:hover { background: #38bdf8; }
"""

class ProductFormDialog(QDialog):
    """Diálogo para adicionar um novo produto"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Novo Produto")
        self.resize(350, 300)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QFormLayout(self)
        
        self.txt_nome = QLineEdit()
        self.cmb_cat = QComboBox()
        self.cmb_cat.addItems(["COMIDA", "BEBIDA", "CANDY", "OUTRO"])
        
        self.txt_preco = QLineEdit("0.00")
        self.txt_custo = QLineEdit("0.00")
        self.txt_estoque_atual = QLineEdit("0")
        self.txt_estoque_min = QLineEdit("10")
        
        layout.addRow("Nome do Produto:", self.txt_nome)
        layout.addRow("Categoria:", self.cmb_cat)
        layout.addRow("Preço Venda (R$):", self.txt_preco)
        layout.addRow("Custo Pago (R$):", self.txt_custo)
        layout.addRow("Qtd Inicial:", self.txt_estoque_atual)
        layout.addRow("Estoque Mínimo:", self.txt_estoque_min)
        
        btn_layout = QHBoxLayout()
        btn_salvar = QPushButton("Salvar Produto")
        btn_salvar.clicked.connect(self.save_product)
        btn_salvar.setStyleSheet("background-color: #16a34a; color: white; padding: 10px; font-weight:bold; border-radius: 4px;")
        btn_layout.addWidget(btn_salvar)
        
        layout.addRow("", btn_layout)

    def save_product(self):
        nome = self.txt_nome.text().strip()
        if not nome:
            QMessageBox.warning(self, "Aviso", "O nome é obrigatório.")
            return

        cat = self.cmb_cat.currentText()
        try:
            preco = float(self.txt_preco.text().replace(',', '.'))
            custo = float(self.txt_custo.text().replace(',', '.'))
            est = int(self.txt_estoque_atual.text())
            est_min = int(self.txt_estoque_min.text())
        except ValueError:
            QMessageBox.warning(self, "Aviso", "Valores numéricos inválidos.")
            return
            
        success, msg = InventoryController.add_product(nome, cat, preco, custo, est, est_min)
        if success:
            QMessageBox.information(self, "Sucesso", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Erro", msg)


class InventoryView(QDialog):
    """Módulo de Gestão de Estoque"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Controle de Estoque - Bomboniere")
        self.resize(850, 600)
        self.setStyleSheet(STYLE_SHEET_INVENTORY)
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_titulo = QLabel("Gestão de Produtos e Estoque")
        lbl_titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #0f172a;")
        layout.addWidget(lbl_titulo)
        
        # Tabela
        self.tbl_produtos = QTableWidget(0, 8)
        self.tbl_produtos.verticalHeader().setVisible(False)
        self.tbl_produtos.verticalHeader().setDefaultSectionSize(45)
        self.tbl_produtos.setHorizontalHeaderLabels([
            "", "ID", "Produto", "Categoria", "Estoque", "Mínimo", "Preço (R$)", "Status"
        ])
        
        header = self.tbl_produtos.horizontalHeader()
        self.tbl_produtos.setColumnWidth(0, 30)
        self.tbl_produtos.setColumnWidth(1, 40)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tbl_produtos.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tbl_produtos)
        
        # Toolbar
        toolbar = QHBoxLayout()
        btn_add = QPushButton("➕ Novo Produto")
        btn_add.setProperty("class", "PrimaryBtn")
        btn_add.clicked.connect(self.new_product)
        
        btn_entrada = QPushButton("📦 Registrar Entrada")
        btn_entrada.setProperty("class", "PrimaryBtn")
        btn_entrada.clicked.connect(self.entrada_estoque)
        
        btn_remover = QPushButton("🗑️ Remover Produto")
        btn_remover.setStyleSheet("background-color: #ef4444; color: white; padding: 10px 15px; border-radius: 4px; font-weight: bold;")
        btn_remover.clicked.connect(self.remover_codigo)
        
        toolbar.addWidget(btn_add)
        toolbar.addWidget(btn_entrada)
        toolbar.addWidget(btn_remover)
        toolbar.addStretch()
        
        layout.addLayout(toolbar)

    def load_data(self):
        produtos = InventoryController.get_all_products()
        self.tbl_produtos.setRowCount(0)
        
        for p in produtos:
            row = self.tbl_produtos.rowCount()
            self.tbl_produtos.insertRow(row)
            
            # Checkbox
            chk_item = QTableWidgetItem("")
            chk_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            chk_item.setCheckState(Qt.CheckState.Unchecked)
            self.tbl_produtos.setItem(row, 0, chk_item)
            
            self.tbl_produtos.setItem(row, 1, QTableWidgetItem(str(p['id'])))
            self.tbl_produtos.setItem(row, 2, QTableWidgetItem(p['nome']))
            self.tbl_produtos.setItem(row, 3, QTableWidgetItem(p['categoria']))
            
            # Formatar estoque
            item_est = QTableWidgetItem(str(p['estoque']))
            if p['status'] == 'BAIXO':
                item_est.setForeground(Qt.GlobalColor.red)
            self.tbl_produtos.setItem(row, 4, item_est)
            
            self.tbl_produtos.setItem(row, 5, QTableWidgetItem(str(p['estoque_min'])))
            self.tbl_produtos.setItem(row, 6, QTableWidgetItem(f"{p['preco']:.2f}"))
            
            item_status = QTableWidgetItem("⚠️ Baixo" if p['status'] == 'BAIXO' else "✅ OK")
            self.tbl_produtos.setItem(row, 7, item_status)

    def new_product(self):
        form = ProductFormDialog(self)
        if form.exec():
            self.load_data()

    def entrada_estoque(self):
        row = self.tbl_produtos.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Selecione um produto na tabela primeiro.")
            return
            
        prod_id = self.tbl_produtos.item(row, 1).text()
        prod_nome = self.tbl_produtos.item(row, 2).text()
        
        from PyQt6.QtWidgets import QInputDialog
        qtd, ok = QInputDialog.getInt(self, "Entrada de Estoque", f"Quantidade a adicionar para:\n{prod_nome}", min=1)
        if ok:
            success, msg = InventoryController.update_stock(prod_id, qtd, "Entrada Manual")
            if success:
                QMessageBox.information(self, "Sucesso", msg)
                self.load_data()
            else:
                QMessageBox.critical(self, "Erro", msg)

    def remover_codigo(self):
        to_remove = []
        names = []
        for row in range(self.tbl_produtos.rowCount()):
            item = self.tbl_produtos.item(row, 0) # Checkbox column
            if item and item.checkState() == Qt.CheckState.Checked:
                to_remove.append(self.tbl_produtos.item(row, 1).text()) # ID column
                names.append(self.tbl_produtos.item(row, 2).text()) # Name column
                
        if not to_remove:
            QMessageBox.warning(self, "Aviso", "Marque pelo menos um produto pelo checkbox para remover.")
            return
            
        nomes_str = ", ".join(names)
        mensagem = f"Tem certeza que deseja apagar {len(to_remove)} produto(s)?\n{nomes_str}"
        if len(mensagem) > 300:
            mensagem = f"Tem certeza que deseja apagar {len(to_remove)} produto(s)?"
            
        reply = QMessageBox.question(self, 'Confirmar', 
                                     mensagem + '\nO histórico financeiro e estoque serão mantidos no sistema.',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            for prod_id in to_remove:
                InventoryController.delete_product(prod_id)
            QMessageBox.information(self, "Sucesso", f"{len(to_remove)} produto(s) removido(s) com sucesso!")
            self.load_data()
