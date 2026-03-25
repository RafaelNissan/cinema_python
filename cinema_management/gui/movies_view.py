import sys
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QMessageBox, QLineEdit, QFormLayout, QComboBox, QTabWidget
)
from PyQt6.QtCore import Qt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from controllers.movies_ctrl import MoviesController

STYLE_SHEET_MOVIES = """
QDialog, QWidget, QTabWidget::pane {
    background-color: #0f172a;
    color: #f8fafc;
    border: none;
}
QTabBar::tab {
    background-color: #1e293b;
    color: #94a3b8;
    padding: 10px 20px;
    font-weight: bold;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}
QTabBar::tab:selected {
    background-color: #3b82f6;
    color: white;
}
QLabel {
    color: #f8fafc;
}
QLineEdit, QComboBox {
    background-color: #1e293b;
    border: 1px solid #334155;
    padding: 8px;
    border-radius: 4px;
    color: #f8fafc;
}
QTableWidget {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 4px;
    color: #f8fafc;
    gridline-color: #334155;
    selection-background-color: #3b82f6;
}
QHeaderView::section {
    background-color: #334155;
    color: #f8fafc;
    font-weight: bold;
    padding: 5px;
    border-bottom: 2px solid #1e293b;
}
QPushButton {
    background-color: #3b82f6;
    color: white;
    font-weight: bold;
    padding: 10px 15px;
    border-radius: 4px;
}
QPushButton:hover { background-color: #2563eb; }
"""

class MovieFormDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cadastrar Filme")
        self.resize(400, 300)
        self.setStyleSheet(STYLE_SHEET_MOVIES)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QFormLayout(self)
        self.txt_titulo = QLineEdit()
        self.cmb_genero = QComboBox()
        self.cmb_genero.addItems(["Ação", "Aventura", "Comédia", "Drama", "Ficção Científica", "Terror", "Romance", "Animação", "Família"])
        self.txt_duracao = QLineEdit("120")
        self.cmb_class = QComboBox()
        self.cmb_class.addItems(["Livre", "10", "12", "14", "16", "18"])
        self.txt_diretor = QLineEdit()
        
        layout.addRow("Título:", self.txt_titulo)
        layout.addRow("Gênero:", self.cmb_genero)
        layout.addRow("Duração (mim):", self.txt_duracao)
        layout.addRow("Classificação:", self.cmb_class)
        layout.addRow("Diretor:", self.txt_diretor)
        
        btn_salvar = QPushButton("Salvar Filme")
        btn_salvar.clicked.connect(self.save)
        layout.addRow("", btn_salvar)

    def save(self):
        t = self.txt_titulo.text()
        d = self.txt_duracao.text()
        if not t or not d.isdigit():
            QMessageBox.warning(self, "Erro", "Título e Duração (numérica) são obrigatórios.")
            return
        success, msg = MoviesController.add_movie(
            t, self.cmb_genero.currentText(), d, 
            self.cmb_class.currentText(), self.txt_diretor.text(), ""
        )
        if success:
            self.accept()
            QMessageBox.information(self, "Sucesso", msg)
        else:
            QMessageBox.critical(self, "Erro", msg)

class SessionFormDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nova Sessão")
        self.resize(350, 250)
        self.setStyleSheet(STYLE_SHEET_MOVIES)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QFormLayout(self)
        self.cmb_filme = QComboBox()
        self.filmes = MoviesController.get_movies()
        for f in self.filmes:
            self.cmb_filme.addItem(f['titulo'], f['id'])
            
        self.cmb_sala = QComboBox()
        self.salas = MoviesController.get_rooms()
        for s in self.salas:
            self.cmb_sala.addItem(s['nome'], s['id'])
            
        from datetime import datetime
        self.txt_data = QLineEdit(datetime.now().strftime("%d/%m/%Y 20:00"))
        self.txt_preco = QLineEdit("30.00")
        
        layout.addRow("Filme:", self.cmb_filme)
        layout.addRow("Sala:", self.cmb_sala)
        layout.addRow("Data e Hora:", self.txt_data)
        layout.addRow("Preço Base (R$):", self.txt_preco)
        
        btn_salvar = QPushButton("Criar Sessão")
        btn_salvar.clicked.connect(self.save)
        layout.addRow("", btn_salvar)

    def save(self):
        f_id = self.cmb_filme.currentData()
        s_id = self.cmb_sala.currentData()
        p = self.txt_preco.text().replace(',', '.')
        
        if not f_id or not s_id:
            QMessageBox.warning(self, "Erro", "Cadastre filmes e salas primeiro.")
            return
            
        success, msg = MoviesController.add_session(f_id, s_id, self.txt_data.text(), p)
        if success:
            self.accept()
            QMessageBox.information(self, "Sucesso", msg)
        else:
            QMessageBox.critical(self, "Erro", msg)

class MoviesView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestão de Filmes e Sessões")
        self.resize(900, 600)
        self.setStyleSheet(STYLE_SHEET_MOVIES)
        
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # --- TAB FILMES ---
        tab_filmes = QWidget()
        lay_filmes = QVBoxLayout(tab_filmes)
        
        btn_add_f = QPushButton("+ Cadastrar Filme")
        btn_add_f.clicked.connect(self.add_filme)
        lay_filmes.addWidget(btn_add_f, alignment=Qt.AlignmentFlag.AlignLeft)
        
        self.tbl_filmes = QTableWidget(0, 5)
        self.tbl_filmes.setHorizontalHeaderLabels(["ID", "Título", "Gênero", "Duração", "Classif."])
        self.tbl_filmes.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        lay_filmes.addWidget(self.tbl_filmes)
        self.tabs.addTab(tab_filmes, "🎬 Filmes")
        
        # --- TAB SALAS ---
        tab_salas = QWidget()
        lay_salas = QVBoxLayout(tab_salas)
        btn_add_s = QPushButton("+ Cadastrar Sala")
        btn_add_s.clicked.connect(self.add_sala)
        lay_salas.addWidget(btn_add_s, alignment=Qt.AlignmentFlag.AlignLeft)
        
        self.tbl_salas = QTableWidget(0, 3)
        self.tbl_salas.setHorizontalHeaderLabels(["ID", "Nome da Sala", "Capacidade"])
        self.tbl_salas.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        lay_salas.addWidget(self.tbl_salas)
        self.tabs.addTab(tab_salas, "💺 Salas")
        
        # --- TAB SESSÕES ---
        tab_sessoes = QWidget()
        lay_sessoes = QVBoxLayout(tab_sessoes)
        btn_add_sess = QPushButton("+ Nova Sessão")
        btn_add_sess.clicked.connect(self.add_sessao)
        lay_sessoes.addWidget(btn_add_sess, alignment=Qt.AlignmentFlag.AlignLeft)
        
        self.tbl_sessoes = QTableWidget(0, 5)
        self.tbl_sessoes.setHorizontalHeaderLabels(["ID", "Filme", "Sala", "Horário", "Preço (R$)"])
        self.tbl_sessoes.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        lay_sessoes.addWidget(self.tbl_sessoes)
        self.tabs.addTab(tab_sessoes, "📆 Sessões")

    def load_data(self):
        # Filmes
        filmes = MoviesController.get_movies()
        self.tbl_filmes.setRowCount(0)
        for f in filmes:
            row = self.tbl_filmes.rowCount()
            self.tbl_filmes.insertRow(row)
            self.tbl_filmes.setItem(row, 0, QTableWidgetItem(str(f['id'])))
            self.tbl_filmes.setItem(row, 1, QTableWidgetItem(f['titulo']))
            self.tbl_filmes.setItem(row, 2, QTableWidgetItem(f['genero']))
            self.tbl_filmes.setItem(row, 3, QTableWidgetItem(f"{f['duracao']} min"))
            self.tbl_filmes.setItem(row, 4, QTableWidgetItem(f['classificacao']))
            
        # Salas
        salas = MoviesController.get_rooms()
        self.tbl_salas.setRowCount(0)
        for s in salas:
            row = self.tbl_salas.rowCount()
            self.tbl_salas.insertRow(row)
            self.tbl_salas.setItem(row, 0, QTableWidgetItem(str(s['id'])))
            self.tbl_salas.setItem(row, 1, QTableWidgetItem(s['nome']))
            self.tbl_salas.setItem(row, 2, QTableWidgetItem(str(s['capacidade'])))
            
        # Sessões
        sessoes = MoviesController.get_sessions()
        self.tbl_sessoes.setRowCount(0)
        for s in sessoes:
            row = self.tbl_sessoes.rowCount()
            self.tbl_sessoes.insertRow(row)
            self.tbl_sessoes.setItem(row, 0, QTableWidgetItem(str(s['id'])))
            self.tbl_sessoes.setItem(row, 1, QTableWidgetItem(s['filme']))
            self.tbl_sessoes.setItem(row, 2, QTableWidgetItem(s['sala']))
            self.tbl_sessoes.setItem(row, 3, QTableWidgetItem(s['data_hora']))
            self.tbl_sessoes.setItem(row, 4, QTableWidgetItem(f"{s['preco']:.2f}"))

    def add_filme(self):
        form = MovieFormDialog(self)
        if form.exec():
            self.load_data()

    def add_sala(self):
        from PyQt6.QtWidgets import QInputDialog
        nome, ok = QInputDialog.getText(self, "Nova Sala", "Nome da Sala (Ex: Sala 1 - IMAX):")
        if ok and nome:
            cap, ok2 = QInputDialog.getInt(self, "Nova Sala", "Capacidade (Assentos):", min=10)
            if ok2:
                success, msg = MoviesController.add_room(nome, cap)
                if success:
                    self.load_data()
                else:
                    QMessageBox.warning(self, "Erro", msg)

    def add_sessao(self):
        form = SessionFormDialog(self)
        if form.exec():
            self.load_data()
