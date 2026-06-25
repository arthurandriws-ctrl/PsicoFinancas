# models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey 
from sqlalchemy.orm import relationship 
from sqlalchemy.sql import func 
from db import Base, engine  # Importa a Base unificada

# Alterado para herdar de Base
class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(50), nullable=False, unique=True)
    email = Column(String(50), nullable=False, unique=True)
    senha = Column(String(255), nullable=False)

class Respondente(Base): 
    __tablename__ = "respondente" 
    id = Column(Integer, primary_key=True, autoincrement=True) 
    faixa_etaria = Column(String(20)) 
    vinculo_senac = Column(String(30)) 
    renda_mensal = Column(String(30)) 
    data_resposta = Column(DateTime, server_default=func.now()) 
    resposta = relationship("Resposta", back_populates="respondente", uselist=False) 
  
class Resposta(Base): 
    __tablename__ = "resposta" 
    id = Column(Integer, primary_key=True, autoincrement=True) 
    id_respondente = Column(Integer, ForeignKey("respondente.id")) 
    anotacao_gastos = Column(String(20)) 
    gasta_mais_que_ganha = Column(String(20)) 
    categoria_gasto = Column(String(30)) 
    compra_impulso = Column(String(20)) 
    tem_orcamento = Column(String(30)) 
    reserva_emergencia = Column(String(40)) 
    controle_financeiro = Column(Integer)        # nota de 1 a 5 
    tem_divida = Column(String(30)) 
    poupa_mensalmente = Column(String(30)) 
    ja_investiu = Column(String(30)) 
    objetivo_financeiro = Column(String(40)) 
    perfil_risco = Column(String(20)) 
    perfil_ia = Column(String(20))               # preenchido pela IA 
    analise_ia = Column(Text)                    # preenchido pela IA 
    respondente = relationship("Respondente", back_populates="resposta") 
    
if __name__ == "__main__": 
    Base.metadata.create_all(engine) 
    print("Todas as tabelas (incluindo usuarios) criadas com sucesso!")
