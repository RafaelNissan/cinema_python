import sys
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget, QLabel, 
    QPushButton, QGridLayout, QMessageBox, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from controllers.sales_ctrl import SalesController

STYLE_SHEETS_SEATS = """
QDialog {
    background-color: #0f172a;
    color: #f8fafc;
}
QLabel {
    color: #f8fafc;
}
QPushButton#SeatBtn {
    background-color: #334155;
    color: white;
    border: none;
    border-radius: 20px;
    font-weight: bold;
    width: 40px;
    height: 40px;
    min-width: 40px;
    min-height: 40px;
}
QPushButton#SeatBtn:hover { background-color: #475569; }
QPushButton#SeatBtn[occupied="true"] {
    background-color: #ef4444;
    color: #fee2e2;
}
QPushButton#SeatBtn[selected="true"] {
    background-color: #22c55e;
    color: #000000;
    font-weight: 900;
}
QFrame#Screen {
    background-color: #3b82f6;
    border-radius: 20px;
    height: 10px;
}
"""

class SeatSelectionDialog(QDialog):
    """Diálogo para seleção de assento interativo"""
    def __init__(self, sessao_id, filme_titulo, sala_nome, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Seleção de Assentos - {filme_titulo}")
        self.setMinimumSize(700, 600)
        self.setStyleSheet(STYLE_SHEETS_SEATS)
        
        self.sessao_id = sessao_id
        self.sala_nome = sala_nome
        self.selected_seat = None
        
        # Ocupados no banco
        self.occupied_seats = SalesController.get_occupied_seats(sessao_id)
        
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Info Header
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.addWidget(QLabel(f"🏠 Sala: {self.sala_nome}"))
        lbl_inst = QLabel("Clique em um assento livre (cinza) para selecionar:")
        lbl_inst.setStyleSheet("color: #94a3b8;")
        info_layout.addWidget(lbl_inst)
        main_layout.addWidget(info_widget)
        
        # Grid area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        grid_widget = QWidget()
        self.grid_layout = QGridLayout(grid_widget)
        self.grid_layout.setSpacing(8)
        
        # Gerar grid 10x10 (A-J) - Invertido: J (atrás) em cima e A (tela) embaixo
        rows = ['J', 'I', 'H', 'G', 'F', 'E', 'D', 'C', 'B', 'A']
        for r_idx, label in enumerate(rows):
            # Row Label
            row_label = QLabel(label)
            row_label.setStyleSheet("font-weight: bold; color: #64748b;")
            self.grid_layout.addWidget(row_label, r_idx, 0)
            
            for c_idx in range(1, 11):
                seat_id = f"{label}{c_idx}"
                btn = QPushButton(str(c_idx))
                btn.setObjectName("SeatBtn")
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                
                if seat_id in self.occupied_seats:
                    btn.setProperty("occupied", "true")
                    btn.setEnabled(False)
                    btn.setStyleSheet("background-color: #ef4444; color: #fee2e2; border-radius: 20px;")
                    btn.setToolTip("Ocupado")
                else:
                    btn.setStyleSheet("background-color: #334155; color: white; border-radius: 20px;")
                    btn.clicked.connect(lambda checked, s=seat_id, b=btn: self.on_seat_clicked(s, b))
                
                self.grid_layout.addWidget(btn, r_idx, c_idx)

        scroll.setWidget(grid_widget)
        main_layout.addWidget(scroll)

        # Screen Area (Agora no final, perto da fileira A)
        main_layout.addSpacing(30)
        lbl_tela = QLabel("TELA")
        lbl_tela.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_tela.setStyleSheet("font-weight: bold; font-size: 14px; color: #3b82f6;")
        main_layout.addWidget(lbl_tela)

        screen_frame = QFrame()
        screen_frame.setObjectName("Screen")
        screen_frame.setFixedHeight(10)
        screen_frame.setStyleSheet("background-color: #3b82f6; border-radius: 5px;")
        main_layout.addWidget(screen_frame)
        main_layout.addSpacing(20)
        
        # Status Legend
        legend_layout = QHBoxLayout()
        legend_layout.addStretch()
        legend_layout.addWidget(self.create_legend_item("Livre", "#334155"))
        legend_layout.addWidget(self.create_legend_item("Ocupado", "#ef4444"))
        legend_layout.addWidget(self.create_legend_item("Selecionado", "#22c55e"))
        legend_layout.addStretch()
        main_layout.addLayout(legend_layout)
        
        # Bottom Actions
        main_layout.addSpacing(20)
        self.btn_confirmar = QPushButton("Confirmar Assento")
        self.btn_confirmar.setStyleSheet("background-color: #3b82f6; color: white; padding: 12px; font-weight: bold; font-size: 15px; border-radius: 6px;")
        self.btn_confirmar.setEnabled(False)
        self.btn_confirmar.clicked.connect(self.accept)
        main_layout.addWidget(self.btn_confirmar)

    def create_legend_item(self, text, color):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        box = QFrame()
        box.setFixedSize(16, 16)
        box.setStyleSheet(f"background-color: {color}; border-radius: 8px;")
        layout.addWidget(box)
        layout.addWidget(QLabel(text))
        return widget

    def on_seat_clicked(self, seat_id, button):
        # Resetar estilos de todos os botões (Nuclear option para garantir o visual)
        for i in range(self.grid_layout.count()):
            w = self.grid_layout.itemAt(i).widget()
            if isinstance(w, QPushButton) and w.objectName() == "SeatBtn":
                if w.property("occupied") == "true":
                    w.setStyleSheet("background-color: #ef4444; color: #fee2e2; border-radius: 20px; font-weight: bold;")
                else:
                    w.setStyleSheet("background-color: #334155; color: white; border-radius: 20px; font-weight: bold;")
        
        # Aplicar o verde vibrante no selecionado
        self.selected_seat = seat_id
        button.setStyleSheet("background-color: #22c55e; color: black; border-radius: 20px; font-weight: 900; border: 2px solid white;")
        
        self.btn_confirmar.setEnabled(True)
        self.btn_confirmar.setText(f"Confirmar Assento: {seat_id}")

    def get_selected_seat(self):
        return self.selected_seat
