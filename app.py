import streamlit as st
from google import genai

# Configuração da página no Streamlit
st.set_page_config(page_title="Valuation Automatizado - B3", layout="wide", page_icon="📊")

st.title("📊 Analista CNPI & Valuation Automatizado (B3)")
st.write("Digite o ticker de qualquer ação da B3 para gerar o relatório completo de Valuation.")

# Campo no menu lateral para a chave e formulário principal
with st.sidebar:
    st.header("Configurações")
    api_key = st.text_input("Insira sua API Key do Google AI Studio:", type="password")
    st.markdown("[Obtenha sua API Key gratuita aqui](https://aistudio.google.com/)")

ticker = st.text_input("Ticker da Ação (ex: BBAS3, ITUB4, WEGE3):").upper()

# Prompt base do seu modelo de análise
PROMPT_BASE = """
Atue como um analista CNPI, gestor de fundos e especialista em valuation com foco na Bolsa de Valores brasileira (B3).
Analise profundamente a ação: {TICKER}.

Objetivo:
Determinar se a empresa está subavaliada, corretamente precificada ou sobreavaliada para um investidor de longo prazo.

Estruture a resposta seguindo exatamente os tópicos abaixo:

# 1. Resumo Executivo
# 2. Modelo de Negócio
# 3. Qualidade da Empresa
# 4. Análise Financeira dos Últimos 5 Anos
# 5. Indicadores Fundamentalistas
# 6. Vantagens Competitivas (Moat)
# 7. Comparação com Concorrentes
# 8. Análise de Endividamento
# 9. Dividendos
# 10. Riscos
# 11. Catalisadores
# 12. Valuation
# 13. Perspectivas para 1, 3 e 5 anos
# 14. Score do Investidor
# 15. Conclusão

Ao final, gere obrigatoriamente a tabela de ranking contendo:
- Nota Final
- Qualidade
- Valuation
- Dividendos
- Crescimento
- Risco
- Preço Justo
- Potencial de Alta (%)
"""

if st.button("Gerar Análise Completa", type="primary"):
    if not api_key:
        st.error("⚠️ Por favor, insira sua API Key no menu lateral à esquerda.")
    elif not ticker:
        st.warning("⚠️ Por favor, digite o ticker da ação.")
    else:
        try:
            with st.spinner(f"O analista IA está processando o valuation completo de {ticker}..."):
                # Conecta à API oficial do Gemini
                client = genai.Client(api_key=api_key)
                
                # Executa a geração do relatório
                prompt_final = PROMPT_BASE.format(TICKER=ticker)
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt_final,
                )
                
                # Exibe o relatório formatado na tela
                st.success("Análise concluída com sucesso!")
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"Ocorreu um erro ao gerar a análise: {e}")
