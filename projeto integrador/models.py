# models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey 
from sqlalchemy.orm import relationship 
from sqlalchemy.sql import func 
from db import Base, engine  # Importa a Base unificada

# Alterado para herdar de Base
class usuario(Base):
    __tablename__ = 'usuario'
    email = Column(String(50), nullable=False, unique=True)
    senha = Column(String(25), nullable=False)
    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(50), nullable=False, unique=True)
    respostas = relationship("repostas", back_populates="usuario")
    perfil = relationship("perfil", back_populates="usuario") 
    resultado = relationship("resultado", back_populates="usuario'")
  
class respostas(Base): 
    __tablename__ = "respostas" 
    id_resposta = Column(Integer, primary_key=True, autoincrement=True) 
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario")) 
    vinculo_senac = Column(String(30)) 
    faixa_etaria = Column(String(20)) 
    renda_mensal = Column(String(30)) 
    data_resposta = Column(DateTime, server_default=func.now()) 
    gastos_mensais = Column(String(20)) 
    salario_ivestido = Column(String(20)) 
    perca_de_investimento = Column(String(30)) 
    uso_do_dinheiro = Column(String(20)) 
    patrimonio_investido = Column(String(30)) 
    opcoes = Column(String(40)) 
    gastos_por_impulso = Column(String(40))        # nota de 1 a 5 
    decisoes_financeiras = Column(String(30)) 
    tempo_investido = Column(String(30)) 
    reserva_emergencial = Column(String(30)) 
    mercado_financeiro = Column(String(40)) 
    produtos_financeiros = Column(String(40)) 
    perfil_ia = Column(String(20))               # preenchido pela IA 
    analise_ia = Column(Text)                    # preenchido pela IA 
    usuario = relationship("usuario", back_populates="respostas") 
    
class perfil(Base):
    __tablename__ = "perfil"
    id_perfil = Column(Integer,primary_key=True,autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario")) 
    nome = Column(String(20))
    perfil = Column(String(20))
    descricao = Column(String(40))
    vinculo = Column(String(20))
    perfil_ia = Column(String(40))
    analise_ia = Column(Text)
    usuario = relationship("usuario", back_populates="perfil") 
    resultado = relationship("resultado", back_populates="perfil") 

class resultado(Base):
    __tablename__ = "resultado"
    id_resultado = Column(Integer, primary_key=True,autoincrement=True)
    id_perfil = Column(Integer , ForeignKey("perfil.id_perfil"))
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario")) 
    perfil = relationship("perfil", back_populates="resultado") 
    usuario = relationship("usuario", back_populates="resultado")








