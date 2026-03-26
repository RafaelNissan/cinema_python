import sys
import os
import pymysql
import pymysql.cursors
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_CONFIG

USER = DB_CONFIG['user']
PASSWORD = DB_CONFIG['password']
HOST = DB_CONFIG['host']
PORT = DB_CONFIG['port']
DB_NAME = DB_CONFIG['database']

BASE_URL = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/"
DATABASE_URL = f"{BASE_URL}{DB_NAME}?charset={DB_CONFIG.get('charset', 'utf8mb4')}"

Base = declarative_base()

class DatabaseConnection:
    """Gerenciador de conexão com suporte a SQLAlchemy e compatibilidade com raw SQL PyMySQL"""
    engine = None
    SessionLocal = None

    @classmethod
    def test_connection(cls):
        try:
            # Tentar conectar no servidor base e criar database se não existir
            engine_base = create_engine(BASE_URL)
            with engine_base.connect() as conn:
                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
            
            cls.engine = create_engine(DATABASE_URL, pool_pre_ping=True)
            cls.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)
            
            with cls.engine.connect() as conn:
                pass
            print(f"[OK] Conectado ao MySQL via SQLAlchemy no banco {DB_NAME}")
            return True
        except Exception as e:
            print(f"[ERRO] Falha ao conectar ao MySQL (SQLAlchemy): {e}")
            return False

    @classmethod
    def create_database_schema(cls, schema_file=None):
        if cls.engine is None:
            if not cls.test_connection():
                return False
        try:
            # Import models carefully to avoid circular imports during setup
            import database.models
            Base.metadata.create_all(bind=cls.engine)
            print("[OK] Schema do banco (SQLAlchemy) atualizado com sucesso!")
            return True
        except Exception as e:
            print(f"[ERRO] Ao criar schema SQLAlchemy: {e}")
            return False

    @staticmethod
    def execute_query(query, params=None, fetch=False, commit=False):
        """Retrocompatibilidade com raw SQL para relatórios e módulos legados."""
        conn = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            port=DB_CONFIG['port'],
            charset=DB_CONFIG['charset'],
            autocommit=commit,
            cursorclass=pymysql.cursors.DictCursor
        )
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                if fetch:
                    return cursor.fetchall()
                return cursor.rowcount
        finally:
            conn.close()

@contextmanager
def get_db():
    if DatabaseConnection.SessionLocal is None:
        DatabaseConnection.test_connection()
    db = DatabaseConnection.SessionLocal()
    try:
        yield db
    finally:
        db.close()