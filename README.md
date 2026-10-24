<div align="center">

# 📈 PsicoFinanças

**Descubra seu perfil financeiro e aprenda a evoluir com a ajuda de IA.**

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
<img src="https://img.shields.io/badge/HTML%2FCSS%2FJS-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML CSS JS" />
<img src="https://img.shields.io/badge/Bootstrap-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white" alt="Bootstrap" />
<img src="https://img.shields.io/badge/Gemini_2.5_Flash-4285F4?style=for-the-badge&logo=googlegemini&logoColor=white" alt="Gemini" />

<br><br>

<img src="https://img.shields.io/badge/Projeto_Integrador-SENAC-004A8D?style=flat-square" alt="SENAC" />
<img src="https://img.shields.io/badge/Desenvolvido_em-equipe-success?style=flat-square" alt="Em equipe" />

</div>

---

## 📖 Sobre o projeto

Desenvolvido no **SENAC** como **projeto integrador** do curso Técnico em Sistemas Operacionais, com foco em aplicações financeiras.

O usuário responde a um **formulário**, o sistema **calcula o perfil financeiro** a partir das respostas e uma **inteligência artificial** (Gemini 2.5 Flash) explica o resultado e oferece dicas para se tornar uma pessoa financeiramente mais responsável.

## 🎯 Objetivos

- Diagnosticar o perfil financeiro do usuário
- Propor dicas e estatísticas personalizadas
- Fornecer ensinamentos para o amadurecimento econômico

## 📸 Demonstração

**Resultado do perfil**

<!-- Mantenha aqui a imagem que você já tem no README atual do repositório -->

**Dashboard**

<!-- Mantenha aqui a imagem que você já tem no README atual do repositório -->

## 🗂️ Estrutura do projeto

```
├── app
│   └── app.py              # Aplicação principal
├── static                  # Estilos (CSS) de cada página
├── templates               # Páginas HTML (cadastro, formulários, perfil, dashboard...)
├── teste                   # Testes
├── db.py                   # Conexão com o banco de dados
├── ia.py                   # Integração com a IA (Gemini)
├── models.py               # Modelos de dados
└── requirements.txt        # Dependências
```

## ⚙️ Como executar

**1. Clone o repositório**

```bash
git clone https://github.com/arthurandriws-ctrl/PsicoFinancas.git
cd PsicoFinancas
```

**2. Instale as dependências**

```bash
pip install -r requirements.txt
```

**3. Configure a chave da API do Google**

Crie um arquivo `.env` na raiz do projeto com o conteúdo:

```env
GEMINI_API_KEY=sua_chave_api
```

> A chave pode ser gerada gratuitamente no [Google AI Studio](https://aistudio.google.com/apikey).
> ⚠️ Nunca envie o arquivo `.env` para o GitHub. Adicione-o ao `.gitignore`.

**4. Inicie a aplicação**

```bash
python app/app.py
```

<!-- Confirme o comando acima e informe o endereço local (ex.: http://localhost:5000) -->

## 👥 Equipe

<!-- Liste os integrantes com link para o GitHub de cada um:
- [Nome](https://github.com/usuario)
-->

## 📬 Contato

Feito por **Arthur Andriws** · [GitHub](https://github.com/arthurandriws-ctrl) · [arthurandriws@gmail.com](mailto:arthurandriws@gmail.com)
