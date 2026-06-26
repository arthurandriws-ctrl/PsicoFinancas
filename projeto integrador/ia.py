# ia.py
import os
import json
from google import genai
from google.genai import types

def analisar_perfil_financeiro(dados_usuario):
    # O cliente obtém automaticamente a GEMINI_API_KEY a partir do ambiente (.env)
    client = genai.Client()
    
    prompt_sistema = """
    Você é um consultor financeiro de IA especializado e empático. 
    Sua tarefa é analisar as respostas do formulário de perfil financeiro de um usuário e gerar um diagnóstico completo.
    
    Você deve obrigatoriamente responder EXCLUSIVAMENTE em formato JSON, sem qualquer texto, bloco de código (como ```json) antes ou depois. 
    O formato deve ser exatamente este:
    {
      "perfil": "Conservador ou Moderado ou Arrojado",
      "analise": "Texto longo formatado sem Markdown (negritos, listas) com a análise detalhada e próximos passos, sem recomendações diretas de compra de ativos (CVM)."
    }
    """
    
    # Junta as respostas do utilizador numa string para enviar à IA
    conteudo_usuario = f"Dados recolhidos no formulário: {dados_usuario}"
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=conteudo_usuario,
        config=types.GenerateContentConfig(
            system_instruction=prompt_sistema,
            temperature=0.5
        )
    )
    
    # Limpa possíveis formatações que a IA possa colocar e converte para dicionário Python
    texto_puro = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(texto_puro)