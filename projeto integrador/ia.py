# ia.py
import os
import json
from google import genai
from google.genai import types # Importação necessária para configurar o formato de saída

def analisar_perfil_financeiro(dados_usuario):
    # O cliente obtém automaticamente a GEMINI_API_KEY a partir do ambiente (.env)
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    MODELO = "gemini-2.5-flash" 
    
    prompt = f"""
    Você é um consultor financeiro. Analise as respostas e responda
    EXCLUSIVAMENTE em JSON, sem texto antes ou depois, com as chaves:
    "perfil" -> uma palavra: Conservador, Moderado ou Arrojado
    "analise" -> 3 parágrafos + 3 sugestões práticas
    
    Respostas do questionário:
    {dados_usuario}
    
    Escreva em português, de forma empática e acessível.
    """
    
    # Chamada utilizando a nova biblioteca com a trava de segurança para JSON
    response = client.models.generate_content(
        model=MODELO, 
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )
    
    texto = response.text.strip()
    texto_puro = texto.replace("```json", "").replace("```", "").strip()
    
    try:
        d = json.loads(texto_puro)
        return {
            "perfil": d.get("perfil", "Indefinido"),
            "analise": d.get("analise", texto_puro)
        }
    except json.JSONDecodeError:
        return {
            "perfil": "Indefinido",
            "analise": texto_puro
        }