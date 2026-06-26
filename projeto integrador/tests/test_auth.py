import unittest
import uuid

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.app import app
from db import SessionLocal
from models import Usuario


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
