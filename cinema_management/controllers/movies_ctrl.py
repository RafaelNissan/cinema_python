import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.connection import get_db
from database.models import Filme, Sala, Sessao

class MoviesController:
    """Controlador para gestão de Filmes, Salas e Sessões"""

    @staticmethod
    def get_movies():
        with get_db() as db:
            filmes = db.query(Filme).order_by(Filme.titulo).all()
            return [{
                'id': f.id,
                'titulo': f.titulo,
                'genero': f.genero,
                'duracao': f.duracao,
                'classificacao': f.classificacao,
                'em_cartaz': f.em_cartaz
            } for f in filmes]

    @staticmethod
    def add_movie(titulo, genero, duracao, classificacao, diretor, sinopse):
        try:
            with get_db() as db:
                novo_filme = Filme(
                    titulo=titulo,
                    genero=genero,
                    duracao=int(duracao),
                    classificacao=classificacao,
                    diretor=diretor,
                    sinopse=sinopse,
                    em_cartaz=True
                )
                db.add(novo_filme)
                db.commit()
                return True, "Filme cadastrado com sucesso!"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_rooms():
        with get_db() as db:
            salas = db.query(Sala).order_by(Sala.nome).all()
            return [{'id': s.id, 'nome': s.nome, 'capacidade': s.capacidade} for s in salas]

    @staticmethod
    def add_room(nome, capacidade):
        try:
            with get_db() as db:
                nova_sala = Sala(nome=nome, capacidade=int(capacidade))
                db.add(nova_sala)
                db.commit()
                return True, "Sala cadastrada com sucesso!"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_sessions():
        with get_db() as db:
            sessoes = db.query(Sessao).order_by(Sessao.data_hora.desc()).all()
            return [{
                'id': s.id,
                'filme': s.filme.titulo if s.filme else "N/A",
                'sala': s.sala.nome if s.sala else "N/A",
                'data_hora': s.data_hora.strftime("%d/%m/%Y %H:%M"),
                'preco': s.preco_base
            } for s in sessoes]

    @staticmethod
    def add_session(filme_id, sala_id, data_hora_str, preco_base):
        try:
            data_hora = datetime.strptime(data_hora_str, "%d/%m/%Y %H:%M")
            with get_db() as db:
                # Buscar a sala para saber a capacidade total
                sala = db.query(Sala).filter(Sala.id == int(sala_id)).first()
                if not sala:
                    return False, "Sala não encontrada."

                sessao = Sessao(
                    filme_id=int(filme_id),
                    sala_id=int(sala_id),
                    data_hora=data_hora,
                    preco_base=float(preco_base),
                    assentos_disponiveis=sala.capacidade
                )
                db.add(sessao)
                db.commit()
                return True, "Sessão cadastrada com sucesso!"
        except ValueError:
            return False, "Formato de data inválido. Use DD/MM/AAAA HH:MM"
        except Exception as e:
            return False, str(e)
