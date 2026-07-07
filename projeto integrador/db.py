
import os

import mysql.connector
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker


def conectar():
    try:
        return mysql.connector.connect(
            host="localhost",
            port=3307,
            user="root",
            password="",
            database="projeto_integrador",
        )
    except mysql.connector.Error:
        return None


DEFAULT_DATABASE_URL = "mysql+pymysql://root:@localhost:3307/projeto_integrador"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def _build_engine():
    if DATABASE_URL.startswith("sqlite"):
        return create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

    engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return engine
    except Exception as exc:
        raise RuntimeError(
            "Não foi possível conectar ao banco MySQL. "
            "Inicie o XAMPP/MySQL ou defina DATABASE_URL para um banco disponível."
        ) from exc


engine = _build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()