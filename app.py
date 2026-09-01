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

# Estilização CSS personalizada para tabelas e negrito
st.markdown("""
<style>
    /* Cabeçalho das tabelas em negrito */
    div[data-testid="stDataFrame"] table thead th {
        font-weight: bold !important;
    }
    /* Primeira coluna (Indicador) das tabelas em negrito */
    div[data-testid="stDataFrame"] table tbody td:nth-child(1) {
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Terminal de Valuation & Análise CNPI (B3)")
st.caption("Automação Fundamentalista de Longo Prazo via Inteligência Artificial")

# Sidebar - Configurações de API Key
with st.sidebar:
    st.header("⚙️ Configurações")
    
    api_key_secret = st.secrets.get("GEMINI_API_KEY", "")
    
    if api_key_secret:
        st.success("🔑 API Key detectada automaticamente!")
        api_key = api_key_secret
    else:
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
        st.error("⚠️ Por favor, insira sua API Key na barra lateral à esquerda ou configure nos Secrets.")
    elif not ticker:
        st.warning("⚠️ Por favor, informe o ticker do ativo.")
    else:
        try:
            with st.spinner(f"🔍 Coletando dados fundamentalistas e calculando valuation para {ticker}..."):
                client = genai.Client(api_key=api_key)
                
                # Prompt Otimizado
                prompt_final = (
                    f"Atue como um analista CNPI, gestor de fundos e especialista em valuation com foco na Bolsa de Valores brasileira (B3).\n"
                    f"Analise profundamente a ação {ticker}.\n\n"
                    "DIRETRIZES FUNDAMENTAIS:\n"
                    "1. Baseie-se nos dados financeiros públicos mais recentes disponíveis.\n"
                    "2. Seja objetivo, analítico e evite jargões desnecessários.\n"
                    "3. Utilize estritamente formatação Markdown (tabelas, negritos e listas) para estruturar a resposta.\n"
                    "4. Para o Valuation (DCF), explicite claramente as premissas matemáticas utilizadas (WACC, taxa de crescimento, etc.) para evitar distorções.\n\n"
                    "Estruture o relatório completo seguindo EXATAMENTE os tópicos abaixo:\n\n"
                    "# 1. Resumo Executivo\n"
                    "- O que a empresa faz e Setor de atuação\n"
                    "- Tese central de investimento\n"
                    "- Principais vantagens competitivas e Principais riscos\n"
                    "- Recomendação final (Compra Forte, Compra, Manutenção, Venda ou Venda Forte)\n"
                    "- Nota final (0 a 10)\n\n"
                    "# 2. Modelo de Negócio\n"
                    "- Como a empresa monetiza e principais produtos/serviços\n"
                    "- Principais clientes e Participação de mercado\n"
                    "- Barreiras de entrada\n"
                    "- Dependência de variáveis macroeconômicas (commodities, juros, dólar, regulação)\n\n"
                    "# 3. Qualidade da Empresa\n"
                    "Avalie Governança corporativa, Histórico da gestão, Alocação de capital e Política de dividendos.\n"
                    "- Atribua notas (0 a 10) para: Governança, Gestão, Eficiência operacional e Alocação de capital.\n\n"
                    "# 4. Análise Financeira (Últimos 5 Anos)\n"
                    "[Apresente uma Tabela Markdown contendo: Receita, EBITDA, Lucro Líquido, Margem EBITDA, Margem Líquida, FCO, FCL, Capex, Dívida Líquida]\n"
                    "- Explique brevemente as tendências encontradas.\n\n"
                    "# 5. Indicadores Fundamentalistas\n"
                    "Apresente e interprete os principais múltiplos (P/L, P/VP, EV/EBITDA, ROE, ROIC, Margens, Div. Yield, Dívida/EBITDA).\n"
                    "- Compare os indicadores com a média do setor e principais concorrentes.\n\n"
                    "# 6. Vantagens Competitivas (Moat)\n"
                    "Avalie a força da Marca, Escala, Custos de troca, Distribuição e Tecnologia. Explique se existe um 'Moat' sustentável.\n\n"
                    "# 7. Comparação Setorial\n"
                    "[Apresente uma Tabela Markdown comparando a empresa com 2 ou 3 concorrentes nas métricas: Receita, Margem EBITDA, ROE, P/L e EV/EBITDA]\n"
                    "- Indique quem é o líder do setor.\n\n"
                    "# 8. Análise de Endividamento\n"
                    "Avalie a qualidade da dívida, prazo médio, indexação e capacidade de pagamento.\n"
                    "- Classifique o Risco de Solidez (Muito Baixo, Baixo, Moderado, Alto, Muito Alto).\n\n"
                    "# 9. Dividendos\n"
                    "Analise o histórico, sustentabilidade (Payout), Yield atual e projeção futura.\n"
                    "- Classifique a qualidade dos dividendos para o longo prazo.\n\n"
                    "# 10. Mapa de Riscos\n"
                    "Liste e classifique de 1 a 5 (onde 5 é o mais crítico) os riscos: Macroeconômico, Regulatório, Operacional, Concorrencial e Governança.\n\n"
                    "# 11. Catalisadores (Triggers)\n"
                    "Identifique 3 a 5 eventos prováveis que podem destravar valor para a ação no curto/médio
