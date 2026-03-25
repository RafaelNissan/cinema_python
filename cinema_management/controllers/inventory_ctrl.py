import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.connection import get_db
from database.models import Produto, EstoqueMovimentacao

class InventoryController:
    """Controlador de Estoque - Lógica de Negócio para Bomboniere"""

    @staticmethod
    def get_all_products():
        """Retorna todos os produtos cadastrados"""
        with get_db() as db:
            produtos = db.query(Produto).order_by(Produto.nome).all()
            return [{
                'id': p.id,
                'nome': p.nome,
                'categoria': p.categoria,
                'preco': p.preco,
                'custo': p.custo,
                'estoque': p.estoque_atual,
                'estoque_min': p.estoque_minimo,
                'status': 'BAIXO' if p.estoque_atual < p.estoque_minimo else 'OK'
            } for p in produtos]
            
    @staticmethod
    def add_product(nome, categoria, preco, custo, estoque, estoque_min):
        """Cadastra um novo produto"""
        try:
            with get_db() as db:
                produto = Produto(
                    nome=nome,
                    categoria=categoria,
                    preco=float(preco),
                    custo=float(custo),
                    estoque_atual=int(estoque),
                    estoque_minimo=int(estoque_min),
                    ativo=True
                )
                db.add(produto)
                
                # Registra movimentação de entrada inicial
                if int(estoque) > 0:
                    db.flush()
                    mov = EstoqueMovimentacao(
                        produto_id=produto.id,
                        tipo='ENTRADA',
                        quantidade=int(estoque),
                        valor_unitario=float(custo),
                        motivo="Cadastro Inicial"
                    )
                    db.add(mov)
                    
                db.commit()
                return True, "Produto cadastrado com sucesso!"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def update_stock(produto_id, quantidade, motivo, tipo='ENTRADA'):
        """Atualiza o estoque de um produto"""
        try:
            with get_db() as db:
                produto = db.query(Produto).filter(Produto.id == produto_id).first()
                if not produto:
                    return False, "Produto não encontrado."
                
                qtd_int = int(quantidade)
                if tipo == 'SAIDA' and produto.estoque_atual - qtd_int < 0:
                    return False, "Estoque insuficiente para esta saída."
                    
                if tipo == 'ENTRADA':
                    produto.estoque_atual += qtd_int
                else:
                    produto.estoque_atual -= qtd_int
                    
                mov = EstoqueMovimentacao(
                    produto_id=produto.id,
                    tipo=tipo,
                    quantidade=qtd_int,
                    valor_unitario=float(produto.custo),
                    motivo=motivo
                )
                db.add(mov)
                
                db.commit()
                return True, "Estoque atualizado com sucesso!"
        except Exception as e:
            return False, str(e)
