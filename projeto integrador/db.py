
import mysql.connector  
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

def conectar():  
    return mysql.connector.connect(
        host="localhost",
        port=3307,          
        user="root",        
        password="",
        database="projeto_integrador"
    )

# 2. Nova estrutura do SQLAlchemy exigida pelo Guia Técnico (usando as mesmas credenciais)
DATABASE_URL = "mysql+pymysql://root:@localhost:3307/projeto_integrador"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()