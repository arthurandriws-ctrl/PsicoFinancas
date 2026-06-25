# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

#importação do arquivo db.py
from db import SessionLocal, engine, Base, conectar
from models import Usuario

app = Flask(__name__)
app.secret_key = 'chave_secreta'

# Garante a criação das tabelas usando o engine importado
Base.metadata.create_all(bind=engine)

def senha_confere(senha_salva, senha_digitada):
    try:
        return check_password_hash(senha_salva, senha_digitada)
    except ValueError:
        return senha_salva == senha_digitada

# Rota primária 
@app.route('/')
def main():
    return render_template('main.html')

# Rota de registro
@app.route('/registrar', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
        
    nome = request.form.get('nome', '').strip()
    email = request.form.get('email', '').strip()
    senha = request.form.get('senhaForm', '').strip() 

    if not nome or not email or not senha:
        flash('Por favor, preencha todos os campos', 'error')
        return render_template('register.html')

    if len(senha) < 8:
        flash('A senha deve ter no mínimo 8 caracteres', 'error')
        return render_template('register.html')

    # Usando a SessionLocal do SQLAlchemy para as consultas do usuário
    session = SessionLocal()
    usuario_existente = session.query(Usuario).filter_by(email=email).first() 
    if usuario_existente:
        flash('Este email já está registrado', 'error')
        session.close()
        return render_template('register.html')

    usuario_existente = session.query(Usuario).filter_by(nome=nome).first() 
    if usuario_existente:
        flash('Este nome de usuário já existe', 'error')
        session.close()
        return render_template('register.html')

    senha_hash = generate_password_hash(senha)
    new_user = Usuario(nome=nome, email=email, senha=senha_hash)
    session.add(new_user)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        flash('Nome ou email já cadastrado', 'error')
        return render_template('register.html')
    finally:
        session.close()

    flash('Usuário registrado com sucesso! Faça login', 'success')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    nome = request.form.get('nomeForm', '').strip()
    email = request.form.get('emailForm', '').strip()
    senha = request.form.get('senhaForm', '')

    if not nome or not email or not senha:
        flash('Por favor, preencha todos os campos', 'error')
        return render_template('login.html')

    session = SessionLocal()
    usuario = session.query(Usuario).filter_by(nome=nome, email=email).first()
    session.close()

    if usuario is None or not senha_confere(usuario.senha, senha):
        flash('Usuário não encontrado', 'error')
        return render_template('login.html')

    flash(f'Bem-vindo, {usuario.nome}!', 'success')
    return redirect(url_for('main'))

if __name__ == '__main__':
    app.run(debug=True)