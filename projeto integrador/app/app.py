import re

from flask import Flask, render_template, request, redirect, url_for, flash, session as flask_session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

#importação do arquivo db.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db import SessionLocal, engine, Base, conectar
from models import Usuario

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = 'chave_secreta'

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Garante a criação das tabelas usando o engine importado
Base.metadata.create_all(bind=engine)

def senha_confere(senha_salva, senha_digitada):
    try:
        return check_password_hash(senha_salva, senha_digitada)
    except ValueError:
        return senha_salva == senha_digitada


def login_obrigatorio(view_func):
    def wrapper(*args, **kwargs):
        if not flask_session.get('usuario_id'):
            flash('Faça login para acessar esta área', 'error')
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper

# Rota primária
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/perfil')
@login_obrigatorio
def perfil():
    return render_template('perfil.html', usuario_nome=flask_session.get('usuario_nome'))

# Rota de registro
@app.route('/registrar', methods=['GET', 'POST']) 
def register():
    if request.method == 'GET':
        return render_template('cadastro.html')
        
    nome = request.form.get('nome', '').strip()
    email = request.form.get('email', '').strip()
    senha = request.form.get('senhaForm', '').strip()
    confirmar_senha = request.form.get('confirmarSenha', '').strip()
    termos = request.form.get('termos')

    if not nome or not email or not senha or not confirmar_senha:
        flash('Por favor, preencha todos os campos', 'error')
        return render_template('cadastro.html')

    if not EMAIL_REGEX.match(email):
        flash('Informe um e-mail válido', 'error')
        return render_template('cadastro.html')

    if len(senha) < 8:
        flash('A senha deve ter no mínimo 8 caracteres', 'error')
        return render_template('cadastro.html')

    if senha != confirmar_senha:
        flash('As senhas não conferem', 'error')
        return render_template('cadastro.html')

    if termos != 'on':
        flash('Você precisa aceitar os termos para se cadastrar', 'error')
        return render_template('cadastro.html')

    email_normalizado = email.lower()
    nome_normalizado = nome.lower()

    db_session = SessionLocal()
    try:
        usuario_existente = db_session.query(Usuario).filter(func.lower(Usuario.email) == email_normalizado).first()
        if usuario_existente:
            flash('Este email já está registrado', 'error')
            return render_template('cadastro.html')

        usuario_existente = db_session.query(Usuario).filter(func.lower(Usuario.nome) == nome_normalizado).first()
        if usuario_existente:
            flash('Este nome de usuário já existe', 'error')
            return render_template('cadastro.html')

        senha_hash = generate_password_hash(senha)
        new_user = Usuario(nome=nome, email=email_normalizado, senha=senha_hash)
        db_session.add(new_user)
        db_session.commit()
    except IntegrityError:
        db_session.rollback()
        flash('Nome ou email já cadastrado', 'error')
        return render_template('cadastro.html')
    finally:
        db_session.close()

    flash('Usuário registrado com sucesso! Faça login', 'success')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('index.html')

    email = request.form.get('emailForm', '').strip().lower()
    senha = request.form.get('senhaForm', '').strip()

    if not email or not senha:
        flash('Por favor, preencha todos os campos', 'error')
        return render_template('index.html')

    db_session = SessionLocal()
    try:
        usuario = db_session.query(Usuario).filter(func.lower(Usuario.email) == email).first()
    finally:
        db_session.close()

    if usuario is None or not senha_confere(usuario.senha, senha):
        flash('E-mail ou senha inválidos', 'error')
        return render_template('index.html')

    flask_session['usuario_id'] = usuario.id
    flask_session['usuario_nome'] = usuario.nome

    flash(f'Bem-vindo, {usuario.nome}!', 'success')
    return redirect(url_for('main'))

if __name__ == '__main__':
    app.run(debug=True)
