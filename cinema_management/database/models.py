import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.connection import Base

class Filme(Base):
    __tablename__ = 'filmes'
    
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255), nullable=False)
    genero = Column(String(100))
    duracao = Column(Integer)  # Em minutos
    classificacao = Column(String(10))
    sinopse = Column(Text)
    diretor = Column(String(150))
    em_cartaz = Column(Boolean, default=True)

class Sala(Base):
    __tablename__ = 'salas'
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), nullable=False)
    capacidade = Column(Integer, nullable=False)

class Sessao(Base):
    __tablename__ = 'sessoes'
    
    id = Column(Integer, primary_key=True, index=True)
    filme_id = Column(Integer, ForeignKey('filmes.id'))
    sala_id = Column(Integer, ForeignKey('salas.id'))
    data_hora = Column(DateTime, nullable=False)
    preco_base = Column(Float, nullable=False)
    assentos_disponiveis = Column(Integer, default=0)
    
    filme = relationship("Filme")
    sala = relationship("Sala")

class ReservaAssento(Base):
    __tablename__ = 'reservas_assentos'
    
    id = Column(Integer, primary_key=True, index=True)
    sessao_id = Column(Integer, ForeignKey('sessoes.id'))
    assento_id = Column(String(10))  # Ex: "A1", "B5"
    status = Column(Enum('LIVRE', 'RESERVADO', 'VENDIDO'), default='LIVRE')

class Produto(Base):
    __tablename__ = 'produtos'
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    categoria = Column(String(100), default='COMIDA')
    preco = Column(Float, nullable=False)
    custo = Column(Float, nullable=False)
    estoque_atual = Column(Integer, default=0)
    estoque_minimo = Column(Integer, default=10)
    ativo = Column(Boolean, default=True)

class Venda(Base):
    __tablename__ = 'vendas'
    
    id = Column(Integer, primary_key=True, index=True)
    funcionario_id = Column(Integer, nullable=True) # Para futura expansão
    forma_pagamento = Column(String(50), nullable=False)
    subtotal = Column(Float, default=0.0)
    desconto = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    total_impostos = Column(Float, default=0.0)
    total_liquido = Column(Float, default=0.0)
    data_venda = Column(DateTime, default=datetime.datetime.now)

class VendaIngresso(Base):
    __tablename__ = 'venda_ingressos'
    
    id = Column(Integer, primary_key=True, index=True)
    venda_id = Column(Integer, ForeignKey('vendas.id'))
    sessao_id = Column(Integer, ForeignKey('sessoes.id'))
    assento_id = Column(String(10))
    tipo_ingresso = Column(String(50))
    preco_unitario = Column(Float)

class VendaProduto(Base):
    __tablename__ = 'venda_produtos'
    
    id = Column(Integer, primary_key=True, index=True)
    venda_id = Column(Integer, ForeignKey('vendas.id'))
    produto_id = Column(Integer, ForeignKey('produtos.id'))
    quantidade = Column(Integer)
    preco_unitario = Column(Float)
    subtotal = Column(Float)

class ImpostoLog(Base):
    __tablename__ = 'impostos_log'
    
    id = Column(Integer, primary_key=True, index=True)
    venda_id = Column(Integer, ForeignKey('vendas.id'))
    iss = Column(Float, default=0.0)
    pis = Column(Float, default=0.0)
    cofins = Column(Float, default=0.0)
    total_impostos = Column(Float, default=0.0)

class EstoqueMovimentacao(Base):
    __tablename__ = 'estoque_movimentacao'
    
    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey('produtos.id'))
    tipo = Column(Enum('ENTRADA', 'SAIDA', 'AJUSTE'), nullable=False)
    quantidade = Column(Integer, nullable=False)
    valor_unitario = Column(Float, default=0.0)
    motivo = Column(String(255))
    data_mov = Column(DateTime, default=datetime.datetime.now)