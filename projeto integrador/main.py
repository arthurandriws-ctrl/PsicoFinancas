from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

from db import db
from models import Usuario

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:suasenha6@localhost/nomedaconexao" #modifica aqui dps
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'chave_secreta'

db.init_app(app)


def senha_confere(senha_salva, senha_digitada):
    try:
        return check_password_hash(senha_salva, senha_digitada)
    except ValueError:
        return senha_salva == senha_digitada


@app.route('/')
def home():
    return 'Salve Fih'


@app.route('/registrar', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    nome = request.form.get('nomeForm', '').strip()
    email = request.form.get('emailForm', '').strip()
    senha = request.form.get('senhaForm', '')

    if not nome or not email or not senha:
        flash('Por favor, preencha todos os campos', 'error')
        return render_template('register.html')

    if len(senha) < 8:
        flash('A senha deve ter no mínimo 8 caracteres', 'error')
        return render_template('register.html')

    usuario_existente = Usuario.query.filter_by(email=email).first() 
    if usuario_existente:
        flash('Este email já está registrado', 'error')
        return render_template('register.html')

    usuario_existente = Usuario.query.filter_by(nome=nome).first() 
    if usuario_existente:
        flash('Este nome de usuário já existe', 'error')
        return render_template('register.html')

    senha_hash = generate_password_hash(senha)
    new_user = Usuario(nome=nome, email=email, senha=senha_hash)
    db.session.add(new_user)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash('Nome ou email já cadastrado', 'error')
        return render_template('register.html')

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

    usuario = Usuario.query.filter_by(nome=nome, email=email).first()

    if usuario is None or not senha_confere(usuario.senha, senha):
        flash('Usuário não encontrado', 'error')
        return render_template('login.html')

    flash(f'Bem-vindo, {usuario.nome}!', 'success')
    return redirect(url_for('home'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)