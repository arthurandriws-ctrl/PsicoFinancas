## 📈 PsicoFinanças
Desenvolvido no SENAC, proposto como **`projeto integrador`** dedicado a área de Técnico em Sistemas Operacionais com aplicações financeiras. 
Possui como objetivo a análise do Perfil Financeiro do usuário com base na coleta de dados por meio de um formulário onde o sistema vai computar
o perfil final com base nas respostas obtidas e contando também com uma inteligência artificial que explica melhor sobre o resultado e oferta dicas
de como se tornar uma pessoa financeiramente responsável.

###  🗂️ Organização das pastas
```
├── app
│   ├── __pycache__
│   └── app.py
├── static
│   └── cadastro.css
│   └── formulario1.css
│   └── formulario2.css
│   └── formulario3.css
│   └── main.css
│   └── perfil.css
│   └── recuperacao.css
│   └── style.css
│   └── termos.css
├── templates
│   └── cadastro.html
│   └── dashboard.html
│   └── formulario1.html
│   └── formulario2.html
│   └── formulario3.html
│   └── main.html
│   └── perfil.html
│   └── recuperacao.html
│   └── style.html
│   └── termos.html
├── teste
├── db.py
├── ia.py
├── models.py
└── requirements.txt
```

## Instalação dos requisitos (requirements.txt)
- Vs Code: <br> 
Abra sua IDE, vá em View(visualizar) e depois abra um novo terminal e copie o código abaixo:

```Bash 
pip insrall -r requirements.txt
```

## Configuração da chave api (.env)
- Vs Code: <br> 
Abra sua IDE, e crie um novo arquivo chamado .env, nele você vai colocar sua chave api da Google

O que colocar no .env:
```Bash 
GEMINI_API_KEY= sua_chave_api
```
#

**`📸 Exemplo de resultado`**
<img width="881" height="1011" alt="Image" src="https://github.com/user-attachments/assets/ce0c32f1-b2c8-418a-b618-e0abbb0f6ec4" />

<br>

**`📸 Exemplo de Dashboard`**
