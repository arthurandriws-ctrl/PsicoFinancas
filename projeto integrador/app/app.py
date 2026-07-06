import re
import json

from flask import Flask, render_template, request, redirect, url_for, flash, session as flask_session, jsonify
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

#importação do arquivo db.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db import SessionLocal, engine, Base, conectar
from models import Usuario, Respondente, Resposta
from ia import analisar_perfil_financeiro

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
    return render_template(
        'perfil.html',
        usuario_nome=flask_session.get('usuario_nome'),
        perfil=flask_session.get('perfil_ia', 'Moderado'),
        analise=flask_session.get('analise_ia', '')
    )


# Redirecionamento revisado pelo grupo do backend
def _get_form_data():
    return flask_session.get('formulario_data', {})


def _has_empty_required_fields(*values):
    for value in values:
        if isinstance(value, (list, tuple, set)):
            if not any(str(item).strip() for item in value):
                return True
        elif value is None:
            return True
        elif isinstance(value, str):
            if not value.strip():
                return True
    return False


def gerar_analise_fallback(form_data):
    perfil = calcular_perfil_fallback(form_data)
    objetivos = form_data.get('objetivos', []) or []
    objetivos_texto = ", ".join(objetivos) if isinstance(objetivos, list) else str(objetivos)
    prazo = form_data.get('prazo_objetivos', '')
    renda = form_data.get('renda_mensal', '')
    idade = form_data.get('idade', '')

    analise = (
        f"Seu perfil financeiro foi estimado como {perfil}. "
        f"Com base nas respostas sobre idade ({idade}), renda mensal ({renda}) e objetivos ({objetivos_texto or 'não informados'}), "
        f"o plano ideal é manter uma abordagem {perfil.lower()} para construir segurança e crescimento. "
        f"O prazo definido para os objetivos é {prazo or 'não informado'}, o que influencia diretamente na escolha de produtos e estratégias mais adequadas."
        f"\n\nSugestões práticas:\n"
        f"- Defina um orçamento mensal e acompanhe os gastos por categoria.\n"
        f"- Reserve uma parte da renda para emergência e investimentos de forma consistente.\n"
        f"- Revise periodicamente seus objetivos e ajuste o plano conforme mudanças de vida."
    )
    return perfil, analise


def calcular_perfil_fallback(form_data):
    score = 0
    preferencia_risco = form_data.get('preferencia_risco', '')
    reacao_a_mercado = form_data.get('reacao_a_mercado', '')
    horizonte_tempo = form_data.get('horizonte_tempo', '')
    patrimonio_investido = form_data.get('patrimonio_investido', '')
    gasta_por_impulso = form_data.get('gasta_por_impulso', '')

    if 'previsibilidade' in preferencia_risco.lower() or 'ganhar pouco' in preferencia_risco.lower():
        score -= 1
    elif 'fortes oscilações' in preferencia_risco.lower():
        score += 1

    if reacao_a_mercado == 'Compraria mais ações':
        score += 1
    elif reacao_a_mercado in ['Venderia todas as minhas ações', 'Venderia parte das minhas ações']:
        score -= 1

    if horizonte_tempo in ['Mais de 5 anos', '5 a 10 anos', 'Mais de 10 anos']:
        score += 1
    elif horizonte_tempo in ['Menos de 1 ano', 'Menos de 2 anos']:
        score -= 1

    if 'quase tudo' in patrimonio_investido.lower():
        score += 1
    elif 'apenas uma parcela' in patrimonio_investido.lower():
        score -= 1

    if gasta_por_impulso == 'Sim':
        score -= 1
    elif gasta_por_impulso == 'Não':
        score += 0

    if score <= -1:
        return 'Conservador'
    elif score >= 1:
        return 'Arrojado'
    return 'Moderado'

@app.route('/formulario1', methods=['GET', 'POST'])
def formulario1():
    if request.method == 'POST':
        form_data = {
            'idade': request.form.get('idade', '').strip(),
            'estado_civil': request.form.get('estado_civil', '').strip(),
            'dependentes': request.form.get('dependentes', '').strip(),
            'profissao': request.form.get('profissao', '').strip(),
            'renda_mensal': request.form.get('renda_mensal', '').strip(),
        }

        if _has_empty_required_fields(*form_data.values()):
            flash('Preencha todos os campos', 'error')
            return render_template('formulario1.html', form_data=form_data)

        flask_session['formulario_data'] = form_data
        return redirect(url_for('formulario2'))

    return render_template('formulario1.html', form_data=_get_form_data())

@app.route('/formulario2', methods=['GET', 'POST'])
def formulario2():
    form_data = _get_form_data()
    if not form_data:
        return redirect(url_for('formulario1'))

    if request.method == 'POST':
        form_data = dict(form_data)
        form_data.update({
            'investimento': request.form.get('investimento', '').strip(),
            'reacao_a_mercado': request.form.get('reacao_a_mercado', '').strip(),
            'horizonte_tempo': request.form.get('horizonte_tempo', '').strip(),
            'patrimonio_investido': request.form.get('patrimonio_investido', '').strip(),
            'preferencia_risco': request.form.get('preferencia_risco', '').strip(),
            'gasta_por_impulso': request.form.get('gasta_por_impulso', '').strip(),
            'decisao_financeira': request.form.get('decisao_financeira', '').strip(),
        })

        if _has_empty_required_fields(
            form_data.get('investimento', ''),
            form_data.get('reacao_a_mercado', ''),
            form_data.get('horizonte_tempo', ''),
            form_data.get('patrimonio_investido', ''),
            form_data.get('preferencia_risco', ''),
            form_data.get('gasta_por_impulso', ''),
            form_data.get('decisao_financeira', ''),
        ):
            flash('Preencha todos os campos', 'error')
            return render_template('formulario2.html', form_data=form_data)

        flask_session['formulario_data'] = form_data
        return redirect(url_for('formulario3'))

    return render_template('formulario2.html', form_data=form_data)

@app.route('/formulario3', methods=['GET', 'POST'])
def formulario3():
    form_data = _get_form_data()
    if not form_data:
        return redirect(url_for('formulario1'))

    if request.method == 'POST':
        form_data = dict(form_data)
        form_data.update({
            'objetivos': request.form.getlist('objetivos'),
            'prazo_objetivos': request.form.get('prazo_objetivos', '').strip(),
        })

        if _has_empty_required_fields(
            form_data.get('objetivos', []),
            form_data.get('prazo_objetivos', ''),
        ):
            flash('Preencha todos os campos', 'error')
            return render_template('formulario3.html', form_data=form_data)

        flask_session['formulario_data'] = form_data

        try:
            dados_usuario = json.dumps(form_data, ensure_ascii=False)
            analise = analisar_perfil_financeiro(dados_usuario)
            perfil_ia = analise.get('perfil', '')
            analise_ia = analise.get('analise', '')
        except Exception:
            perfil_ia = ''
            analise_ia = ''

        if perfil_ia not in ['Conservador', 'Moderado', 'Arrojado']:
            perfil_ia, analise_ia = gerar_analise_fallback(form_data)
            if not analise_ia:
                analise_ia = f"A IA não retornou um perfil definitivo, mas com base nas respostas seu perfil financeiro estimado é {perfil_ia}."

        flask_session['perfil_ia'] = perfil_ia
        flask_session['analise_ia'] = analise_ia

        db_session = SessionLocal()
        try:
            respondente = Respondente(
                faixa_etaria=form_data.get('idade', ''),
                vinculo_senac=form_data.get('estado_civil', ''),
                renda_mensal=form_data.get('renda_mensal', ''),
            )
            db_session.add(respondente)
            db_session.commit()

            resposta = Resposta(
                id_respondente=respondente.id,
                anotacao_gastos=form_data.get('reacao_a_mercado', ''),
                gasta_mais_que_ganha=form_data.get('gasta_por_impulso', ''),
                categoria_gasto=form_data.get('preferencia_risco', ''),
                compra_impulso=form_data.get('gasta_por_impulso', ''),
                tem_orcamento=form_data.get('horizonte_tempo', ''),
                reserva_emergencia=form_data.get('patrimonio_investido', ''),
                controle_financeiro=None,
                tem_divida='Não informado',
                poupa_mensalmente='Não informado',
                ja_investiu=form_data.get('preferencia_risco', ''),
                objetivo_financeiro=', '.join(form_data.get('objetivos', [])),
                perfil_ia=perfil_ia,
                analise_ia=analise_ia,
            )
            db_session.add(resposta)
            db_session.commit()
        finally:
            db_session.close()

        return redirect(url_for('perfil'))

    return render_template('formulario3.html', form_data=form_data)

@app.route('/recuperacao')
def recuperacao():
    return render_template('recuperacao.html')

@app.route('/termos')
def termos():
    return render_template('termos.html')

@app.route('/avaliar', methods=['POST'])
@login_obrigatorio
def avaliar():
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({'error': 'JSON inválido'}), 400

    if not flask_session.get('usuario_id'):
        return jsonify({'error': 'Faça login para enviar o formulário'}), 401

    try:
        ia_result = analisar_perfil_financeiro(dados)
        flask_session['perfil_ia'] = ia_result.get('perfil', '')
        flask_session['analise_ia'] = ia_result.get('analise', '')
        return jsonify(ia_result)
    except Exception as e:
        return jsonify({'error': 'Erro ao processar dados', 'detail': str(e)}), 500

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