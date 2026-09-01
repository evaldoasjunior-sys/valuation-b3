import streamlit as st
import json
import re
import pandas as pd
import plotly.express as px
from google import genai

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Valuation - B3", 
    layout="wide", 
    page_icon="📈",
    initial_sidebar_state="expanded"
)

# Estilização CSS customizada
st.markdown("""
<style>
    .metric-card {
        background-color: #1E222D;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #2A2E39;
        text-align: center;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #00E676;
    }
    .metric-label {
        font-size: 14px;
        color: #B2B5BE;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Terminal de Valuation & Análise CNPI (B3)")
st.caption("Automação Fundamentalista de Longo Prazo via Inteligência Artificial")

# Sidebar - Configurações
with st.sidebar:
    st.header("⚙️ Configurações")
    api_key = st.text_input("Insira sua API Key do Google AI Studio:", type="password")
    st.markdown("[Obtenha sua API Key gratuita aqui](https://aistudio.google.com/)")
    st.divider()
    st.info("💡 **Dica:** Digite tickers da B3 como BBAS3, ITUB4, WEGE3, PETR4 ou VALE3.")

# Entrada principal
col_input, col_btn = st.columns([3, 1])
with col_input:
    ticker = st.text_input("Ticker da Ação:", placeholder="Ex: BBAS3").upper()
with col_btn:
    st.write(" ")
    st.write(" ")
    btn_analisar = st.button("🚀 Gerar Dashboard", type="primary", use_container_width=True)

if btn_analisar:
    if not api_key:
        st.error("⚠️ Por favor, insira sua API Key na barra lateral à esquerda.")
    elif not ticker:
        st.warning("⚠️ Por favor, informe o ticker do ativo.")
    else:
        try:
            with st.spinner(f"🔍 Coletando dados fundamentalistas e calculando valuation para {ticker}..."):
                client = genai.Client(api_key=api_key)
                
                # Prompt formatado com f-string limpa
                prompt_final = f"""
Atue como um analista CNPI, gestor de fundos e especialista em valuation na B3.
Analise profundamente a ação: {ticker}.

No final do relatório, inclua OBRIGATORIAMENTE um bloco de código JSON isolado contendo exatamente esta estrutura para alimentarmos o dashboard gráfico:

```json
{{
  "nota_final": 8.5,
  "qualidade": 8.5,
  "valuation": 9.0,
  "dividendos": 9.5,
  "crescimento": 7.5,
  "risco": 3.0,
  "preco_justo": 36.00,
  "potencial_alta_pct": 33.3,
  "recomendacao": "COMPRA"
}}
