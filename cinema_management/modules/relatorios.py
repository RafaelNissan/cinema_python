# modules/relatorios.py
"""
Módulo de Relatórios e Dashboards
"""
from datetime import datetime, timedelta
from decimal import Decimal
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import DatabaseConnection


class Relatorios:
    """Classe para gerar relatórios do sistema"""

    @staticmethod
    def vendas_por_periodo(data_inicio, data_fim):
        """
        Relatório de vendas por período

        Returns:
            dict com estatísticas do período
        """
        query = """
            SELECT 
                COUNT(*) as total_vendas,
                SUM(subtotal) as total_bruto,
                SUM(desconto) as total_descontos,
                SUM(total) as total_liquido,
                SUM(total_impostos) as total_impostos,
                AVG(total) as ticket_medio,
                forma_pagamento,
                COUNT(*) as qtd_por_forma
            FROM vendas
            WHERE DATE(data_venda) BETWEEN %s AND %s
            GROUP BY forma_pagamento
        """

        resultados = DatabaseConnection.execute_query(
            query, (data_inicio, data_fim), fetch=True
        )

        # Calcular totais gerais
        query_total = """
            SELECT 
                COUNT(*) as total_vendas,
                SUM(subtotal) as faturamento_bruto,
                SUM(desconto) as descontos,
                SUM(total) as faturamento_liquido,
                SUM(total_impostos) as impostos,
                AVG(total) as ticket_medio
            FROM vendas
            WHERE DATE(data_venda) BETWEEN %s AND %s
        """

        total = DatabaseConnection.execute_query(
            query_total, (data_inicio, data_fim), fetch=True
        )[0]

        return {
            'periodo': {
                'inicio': data_inicio,
                'fim': data_fim
            },
            'resumo': total,
            'por_forma_pagamento': resultados
        }

    @staticmethod
    def produtos_mais_vendidos(data_inicio=None, data_fim=None, limit=10):
        """
        Relatório dos produtos mais vendidos

        Args:
            data_inicio: Data inicial (None = últimos 30 dias)
            data_fim: Data final (None = hoje)
            limit: Quantidade de produtos a retornar
        """
        if data_fim is None:
            data_fim = datetime.now().date()
        if data_inicio is None:
            data_inicio = data_fim - timedelta(days=30)

        query = """
            SELECT 
                p.nome as produto,
                p.categoria,
                SUM(vp.quantidade) as quantidade_vendida,
                SUM(vp.subtotal) as receita_total,
                AVG(vp.preco_unitario) as preco_medio
            FROM venda_produtos vp
            INNER JOIN produtos p ON vp.produto_id = p.id
            INNER JOIN vendas v ON vp.venda_id = v.id
            WHERE DATE(v.data_venda) BETWEEN %s AND %s
            GROUP BY p.id, p.nome, p.categoria
            ORDER BY quantidade_vendida DESC
            LIMIT %s
        """

        return DatabaseConnection.execute_query(
            query, (data_inicio, data_fim, limit), fetch=True
        )

    @staticmethod
    def filmes_mais_vendidos(data_inicio=None, data_fim=None, limit=10):
        """Relatório dos filmes mais assistidos"""
        if data_fim is None:
            data_fim = datetime.now().date()
        if data_inicio is None:
            data_inicio = data_fim - timedelta(days=30)

        query = """
            SELECT 
                f.titulo,
                f.genero,
                COUNT(vi.id) as ingressos_vendidos,
                SUM(vi.preco_unitario) as receita_total,
                COUNT(DISTINCT s.id) as sessoes_realizadas
            FROM filmes f
            INNER JOIN sessoes s ON f.id = s.filme_id
            INNER JOIN venda_ingressos vi ON s.id = vi.sessao_id
            INNER JOIN vendas v ON vi.venda_id = v.id
            WHERE DATE(v.data_venda) BETWEEN %s AND %s
            GROUP BY f.id, f.titulo, f.genero
            ORDER BY ingressos_vendidos DESC
            LIMIT %s
        """

        return DatabaseConnection.execute_query(
            query, (data_inicio, data_fim, limit), fetch=True
        )

    @staticmethod
    def estoque_atual():
        """Relatório de estoque atual com alertas"""
        query = """
            SELECT 
                id, nome, categoria, 
                estoque_atual, estoque_minimo,
                preco, custo,
                (estoque_atual * custo) as valor_estoque,
                CASE 
                    WHEN estoque_atual < estoque_minimo THEN 'CRÍTICO'
                    WHEN estoque_atual < (estoque_minimo * 1.5) THEN 'BAIXO'
                    ELSE 'OK'
                END as status
            FROM produtos
            WHERE ativo = TRUE
            ORDER BY 
                CASE 
                    WHEN estoque_atual < estoque_minimo THEN 1
                    WHEN estoque_atual < (estoque_minimo * 1.5) THEN 2
                    ELSE 3
                END,
                nome
        """

        return DatabaseConnection.execute_query(query, fetch=True)

    @staticmethod
    def dashboard_hoje():
        """Dashboard com informações do dia atual"""
        hoje = datetime.now().date()

        # Vendas de hoje
        query_vendas = """
            SELECT 
                COUNT(*) as total_vendas,
                COALESCE(SUM(total), 0) as faturamento,
                COALESCE(SUM(total_liquido), 0) as liquido,
                COALESCE(AVG(total), 0) as ticket_medio
            FROM vendas
            WHERE DATE(data_venda) = %s
        """
        vendas = DatabaseConnection.execute_query(query_vendas, (hoje,), fetch=True)[0]

        # Ingressos vendidos hoje
        query_ingressos = """
            SELECT COUNT(*) as total_ingressos
            FROM venda_ingressos vi
            INNER JOIN vendas v ON vi.venda_id = v.id
            WHERE DATE(v.data_venda) = %s
        """
        ingressos = DatabaseConnection.execute_query(query_ingressos, (hoje,), fetch=True)[0]

        # Produtos vendidos hoje
        query_produtos = """
            SELECT SUM(quantidade) as total_produtos
            FROM venda_produtos vp
            INNER JOIN vendas v ON vp.venda_id = v.id
            WHERE DATE(v.data_venda) = %s
        """
        produtos = DatabaseConnection.execute_query(query_produtos, (hoje,), fetch=True)[0]

        # Produtos com estoque baixo
        query_estoque_baixo = """
            SELECT COUNT(*) as produtos_criticos
            FROM produtos
            WHERE estoque_atual < estoque_minimo AND ativo = TRUE
        """
        estoque = DatabaseConnection.execute_query(query_estoque_baixo, fetch=True)[0]

        return {
            'data': hoje,
            'vendas': vendas,
            'ingressos': ingressos,
            'produtos': produtos,
            'alertas_estoque': estoque
        }

    @staticmethod
    def faturamento_mensal(ano=None, mes=None):
        """Faturamento detalhado do mês"""
        if ano is None:
            ano = datetime.now().year
        if mes is None:
            mes = datetime.now().month

        query = """
            SELECT 
                DATE(data_venda) as data,
                COUNT(*) as vendas,
                SUM(total) as faturamento_bruto,
                SUM(total_liquido) as faturamento_liquido,
                SUM(total_impostos) as impostos
            FROM vendas
            WHERE YEAR(data_venda) = %s AND MONTH(data_venda) = %s
            GROUP BY DATE(data_venda)
            ORDER BY data
        """

        return DatabaseConnection.execute_query(query, (ano, mes), fetch=True)

    @staticmethod
    def impostos_detalhado(data_inicio, data_fim):
        """Relatório detalhado de impostos"""
        query = """
            SELECT 
                DATE(v.data_venda) as data,
                COUNT(v.id) as total_vendas,
                SUM(il.iss) as total_iss,
                SUM(il.pis) as total_pis,
                SUM(il.cofins) as total_cofins,
                SUM(il.total_impostos) as total_impostos,
                SUM(v.total) as faturamento_bruto,
                SUM(v.total_liquido) as faturamento_liquido
            FROM impostos_log il
            INNER JOIN vendas v ON il.venda_id = v.id
            WHERE DATE(v.data_venda) BETWEEN %s AND %s
            GROUP BY DATE(v.data_venda)
            ORDER BY data
        """

        resultados = DatabaseConnection.execute_query(
            query, (data_inicio, data_fim), fetch=True
        )

        # Totais do período
        if resultados:
            total_iss = sum(r['total_iss'] for r in resultados)
            total_pis = sum(r['total_pis'] for r in resultados)
            total_cofins = sum(r['total_cofins'] for r in resultados)
            total_impostos = sum(r['total_impostos'] for r in resultados)
            total_bruto = sum(r['faturamento_bruto'] for r in resultados)

            return {
                'detalhado': resultados,
                'resumo': {
                    'total_iss': total_iss,
                    'total_pis': total_pis,
                    'total_cofins': total_cofins,
                    'total_impostos': total_impostos,
                    'faturamento_bruto': total_bruto,
                    'percentual_impostos': (total_impostos / total_bruto * 100) if total_bruto > 0 else 0
                }
            }
        return {'detalhado': [], 'resumo': {}}

if __name__ == "__main__":
    # Teste de relatórios
    print("=" * 60)
    print("DASHBOARD DE HOJE")
    print("=" * 60)

    dashboard = Relatorios.dashboard_hoje()
    print(f"\nData: {dashboard['data']}")
    print(f"Total de vendas: {dashboard['vendas']['total_vendas']}")
    print(f"Faturamento: R$ {dashboard['vendas']['faturamento']:.2f}")
    print(f"Ingressos vendidos: {dashboard['ingressos']['total_ingressos']}")
    print(f"Produtos vendidos: {dashboard['produtos']['total_produtos'] or 0}")
    print(f"Alertas de estoque: {dashboard['alertas_estoque']['produtos_criticos']}")