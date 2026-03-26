import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.connection import get_db
from database.models import Sessao, Filme, Sala, Produto, Venda, VendaIngresso, VendaProduto, ImpostoLog, ReservaAssento
from config import IMPOSTOS, TIPOS_INGRESSO

class SalesController:
    """Controlador de Vendas - Lógica de Negócio para o PDV"""

    @staticmethod
    def get_upcoming_sessions():
        """Retorna sessões futuras para venda de ingressos"""
        with get_db() as db:
            sessoes = db.query(Sessao).filter(Sessao.data_hora >= datetime.now()).all()
            resultados = []
            for s in sessoes:
                resultados.append({
                    'id': s.id,
                    'filme': s.filme.titulo if s.filme else 'Desconhecido',
                    'sala': s.sala.nome if s.sala else 'Desconhecida',
                    'horario': s.data_hora.strftime('%d/%m %H:%M'),
                    'preco': s.preco_base
                })
            return resultados

    @staticmethod
    def get_products():
        """Retorna produtos da bomboniere para venda"""
        with get_db() as db:
            produtos = db.query(Produto).filter(Produto.ativo == True).all()
            return [{
                'id': p.id,
                'nome': p.nome,
                'categoria': p.categoria,
                'preco': p.preco,
                'estoque': p.estoque_atual
            } for p in produtos]
            
    @staticmethod
    def calculate_totals(ingressos, produtos):
        """
        Calcula subtotais e impostos.
        ingressos: list de dicts {'preco_base': float, 'tipo': 'INTEIRA|MEIA'}
        produtos: list de dicts {'preco': float, 'quantidade': int}
        """
        subtotal = 0.0
        
        # Calcular ingressos
        for ing in ingressos:
            mult = TIPOS_INGRESSO.get(ing['tipo'], 1.0)
            subtotal += float(ing['preco_base']) * float(mult)
            
        # Calcular produtos
        for prod in produtos:
            subtotal += float(prod['preco']) * int(prod['quantidade'])
            
        # Impostos
        iss = subtotal * IMPOSTOS['ISS']
        pis = subtotal * IMPOSTOS['PIS']
        cofins = subtotal * IMPOSTOS['CONFINS'] # O config antigo tem erro de digitação CONFINS
        total_impostos = iss + pis + cofins
        total_liquido = subtotal - total_impostos
        
        return {
            'subtotal': subtotal,
            'total_impostos': total_impostos,
            'total_liquido': total_liquido,
            'iss': iss,
            'pis': pis,
            'cofins': cofins
        }

    @staticmethod
    def process_sale(forma_pagamento, ingressos, produtos, funcionario_id=None):
        """Processa a venda, baixa estoque e gera os registros no DB"""
        totais = SalesController.calculate_totals(ingressos, produtos)
        
        if totais['subtotal'] == 0:
            return False, "Venda vazia."
            
        try:
            with get_db() as db:
                nova_venda = Venda(
                    funcionario_id=funcionario_id,
                    forma_pagamento=forma_pagamento,
                    subtotal=totais['subtotal'],
                    desconto=0.0,
                    total=totais['subtotal'],
                    total_impostos=totais['total_impostos'],
                    total_liquido=totais['total_liquido']
                )
                db.add(nova_venda)
                db.flush() # Para pegar o ID da venda
                
                # Registrar Ingressos
                for ing in ingressos:
                    mult = TIPOS_INGRESSO.get(ing['tipo'], 1.0)
                    preco_final = float(ing['preco_base']) * float(mult)
                    vi = VendaIngresso(
                        venda_id=nova_venda.id,
                        sessao_id=ing['sessao_id'],
                        tipo_ingresso=ing['tipo'],
                        preco_unitario=preco_final
                    )
                    db.add(vi)
                    
                # Registrar Produtos e Baixar Estoque
                for prod in produtos:
                    vp = VendaProduto(
                        venda_id=nova_venda.id,
                        produto_id=prod['id'],
                        quantidade=prod['quantidade'],
                        preco_unitario=prod['preco'],
                        subtotal=float(prod['preco']) * int(prod['quantidade'])
                    )
                    db.add(vp)
                    
                    # Atualizar Estoque
                    db_prod = db.query(Produto).filter(Produto.id == prod['id']).first()
                    if db_prod:
                        db_prod.estoque_atual -= prod['quantidade']
                
                # Log de Impostos
                imposto_log = ImpostoLog(
                    venda_id=nova_venda.id,
                    iss=totais['iss'],
                    pis=totais['pis'],
                    cofins=totais['cofins'],
                    total_impostos=totais['total_impostos']
                )
                db.add(imposto_log)
                
                db.commit()
                return True, nova_venda.id
        except Exception as e:
            return False, f"Erro ao processar venda: {str(e)}"

    @staticmethod
    def get_sales_history():
        """Busca as últimas 500 vendas"""
        with get_db() as db:
            from database.models import Venda
            vendas = db.query(Venda).order_by(Venda.data_venda.desc()).limit(500).all()
            return [{
                'id': v.id,
                'data': v.data_venda.strftime("%d/%m/%Y %H:%M"),
                'pagamento': v.forma_pagamento,
                'bruto': v.subtotal,
                'impostos': v.total_impostos,
                'liquido': v.total_liquido
            } for v in vendas]
