import os
import unittest
import uuid
from unittest.mock import patch

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ.setdefault("DATABASE_URL", "sqlite:///./psicofinancas_test.db")

from app.app import app
from db import SessionLocal
from models import Usuario, Respondente, Resposta


class AuthFlowTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.email = f"auth_test_{uuid.uuid4().hex[:8]}@example.com"
        self.password = "Senha1234"

    def tearDown(self):
        session = SessionLocal()
        session.query(Usuario).filter(Usuario.email == self.email).delete()
        session.commit()
        session.close()

    def test_register_rejects_password_mismatch(self):
        response = self.client.post(
            "/registrar",
            data={
                "nome": "Usuário Teste",
                "email": self.email,
                "senhaForm": self.password,
                "confirmarSenha": "OutraSenha123",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("As senhas não conferem", response.get_data(as_text=True))

    def test_register_requires_terms_acceptance(self):
        response = self.client.post(
            "/registrar",
            data={
                "nome": "Usuário Teste",
                "email": self.email,
                "senhaForm": self.password,
                "confirmarSenha": self.password,
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("aceitar os termos", response.get_data(as_text=True))

    def test_home_shows_login_page(self):
        response = self.client.get("/", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Faça login", response.get_data(as_text=True))

    def test_profile_requires_login(self):
        response = self.client.get("/perfil", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("login", response.get_data(as_text=True).lower())

    def test_profile_is_available_after_form_completion_without_login(self):
        self.client.post(
            "/formulario1",
            data={"idade": "30", "estado_civil": "Solteiro(a)", "dependentes": "0", "profissao": "Analista", "renda_mensal": "3000"},
        )
        self.client.post(
            "/formulario2",
            data={"investimento": "Inferior a 25%", "reacao_a_mercado": "Não faria nada", "horizonte_tempo": "Mais de 5 anos", "patrimonio_investido": "Uma parte importante", "preferencia_risco": "Ganhar pouco, mas com previsibilidade", "gasta_por_impulso": "Não", "decisao_financeira": "Analiso antes de decidir"},
        )
        response = self.client.post(
            "/formulario3",
            data={"objetivos": ["Comprar um imóvel"], "prazo_objetivos": "3 a 5 anos"},
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        profile_response = self.client.get("/perfil")
        self.assertEqual(profile_response.status_code, 200)
        self.assertIn("Resultado da Análise", profile_response.get_data(as_text=True))

    def test_formulario1_requires_all_fields(self):
        response = self.client.post("/formulario1", data={"idade": "", "estado_civil": "", "dependentes": "", "profissao": "", "renda_mensal": ""})

        self.assertEqual(response.status_code, 200)
        self.assertIn("Preencha todos os campos", response.get_data(as_text=True))

    def test_formulario2_requires_all_fields(self):
        self.client.post(
            "/formulario1",
            data={"idade": "30", "estado_civil": "Solteiro(a)", "dependentes": "0", "profissao": "Analista", "renda_mensal": "3000"},
        )

        response = self.client.post(
            "/formulario2",
            data={"investimento": "", "reacao_a_mercado": "", "horizonte_tempo": "", "patrimonio_investido": "", "preferencia_risco": "", "gasta_por_impulso": "", "decisao_financeira": ""},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Preencha todos os campos", response.get_data(as_text=True))

    def test_formulario2_renders_client_side_validation(self):
        self.client.post(
            "/formulario1",
            data={"idade": "30", "estado_civil": "Solteiro(a)", "dependentes": "0", "profissao": "Analista", "renda_mensal": "3000"},
        )

        response = self.client.get("/formulario2")

        self.assertEqual(response.status_code, 200)
        self.assertIn("validarFormulario2", response.get_data(as_text=True))

    def test_formulario3_requires_all_fields(self):
        self.client.post(
            "/formulario1",
            data={"idade": "30", "estado_civil": "Solteiro(a)", "dependentes": "0", "profissao": "Analista", "renda_mensal": "3000"},
        )
        self.client.post(
            "/formulario2",
            data={"investimento": "Inferior a 25%", "reacao_a_mercado": "Não faria nada", "horizonte_tempo": "Mais de 5 anos", "patrimonio_investido": "Uma parte importante", "preferencia_risco": "Ganhar pouco, mas com previsibilidade", "gasta_por_impulso": "Não", "decisao_financeira": "Analiso antes de decidir"},
        )

        response = self.client.post(
            "/formulario3",
            data={"objetivos": [], "prazo_objetivos": ""},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Preencha todos os campos", response.get_data(as_text=True))

    def test_formulario3_creates_detailed_report_when_ai_fails(self):
        self.client.post(
            "/formulario1",
            data={"idade": "30", "estado_civil": "Solteiro(a)", "dependentes": "0", "profissao": "Analista", "renda_mensal": "3000"},
        )
        self.client.post(
            "/formulario2",
            data={"investimento": "Inferior a 25%", "reacao_a_mercado": "Não faria nada", "horizonte_tempo": "Mais de 5 anos", "patrimonio_investido": "Uma parte importante", "preferencia_risco": "Ganhar pouco, mas com previsibilidade", "gasta_por_impulso": "Não", "decisao_financeira": "Analiso antes de decidir"},
        )

        with patch("app.app.analisar_perfil_financeiro", side_effect=RuntimeError("IA indisponível")):
            response = self.client.post(
                "/formulario3",
                data={"objetivos": ["Comprar um imóvel"], "prazo_objetivos": "3 a 5 anos"},
                follow_redirects=False,
            )

        self.assertEqual(response.status_code, 302)
        with self.client.session_transaction() as session:
            self.assertIn("Sugestões práticas", session.get("analise_ia", ""))

    def test_dashboard_shows_profile_statistics_from_database(self):
        session = SessionLocal()
        try:
            session.query(Resposta).delete()
            session.query(Respondente).delete()
            session.commit()

            respondente1 = Respondente(faixa_etaria="30", vinculo_senac="Solteiro(a)", renda_mensal="3000")
            respondente2 = Respondente(faixa_etaria="35", vinculo_senac="Casado(a)", renda_mensal="5000")
            respondente3 = Respondente(faixa_etaria="40", vinculo_senac="Divorciado(a)", renda_mensal="7000")
            session.add_all([respondente1, respondente2, respondente3])
            session.commit()

            session.add_all([
                Resposta(id_respondente=respondente1.id, perfil_ia="Arrojado"),
                Resposta(id_respondente=respondente2.id, perfil_ia="Moderado"),
                Resposta(id_respondente=respondente3.id, perfil_ia="Conservador"),
            ])
            session.commit()

            response = self.client.get('/dashboard')
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('Estatísticas dos perfis financeiros', html)
            self.assertIn('3', html)
            self.assertIn('33.3%', html)

            persisted_total = session.query(Resposta).count()
            self.assertEqual(persisted_total, 3)
        finally:
            session.query(Resposta).delete()
            session.query(Respondente).delete()
            session.commit()
            session.close()

    def test_register_and_login_success(self):
        register_response = self.client.post(
            "/registrar",
            data={
                "nome": "Usuário Teste",
                "email": self.email,
                "senhaForm": self.password,
                "confirmarSenha": self.password,
                "termos": "on",
            },
            follow_redirects=True,
        )

        self.assertEqual(register_response.status_code, 200)
        self.assertIn("registrado com sucesso", register_response.get_data(as_text=True))

        login_response = self.client.post(
            "/login",
            data={"emailForm": self.email, "senhaForm": self.password},
            follow_redirects=False,
        )

        self.assertEqual(login_response.status_code, 302)
        self.assertEqual(login_response.headers["Location"], "/main")

        follow_up = self.client.get(login_response.headers["Location"])
        self.assertEqual(follow_up.status_code, 200)
        self.assertIn("Bem-vindo", follow_up.get_data(as_text=True))
        self.assertIn("PsicoFinanças", follow_up.get_data(as_text=True))

        profile_response = self.client.get("/perfil")
        self.assertEqual(profile_response.status_code, 200)
        self.assertIn("Perfil", profile_response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
