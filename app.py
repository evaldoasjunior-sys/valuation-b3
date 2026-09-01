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

# Estilização CSS customizada para visual de Terminal Financeiro
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

# Sidebar - Configurações e Modos de Navegação
with st.sidebar:
    st.header("⚙️ Configurações")
    api_key = st.text_input("Insira sua API Key do Google AI Studio:", type="password")
    st.markdown("[Obtenha sua API Key gratuita aqui](https://aistudio.google.com/)")
    st.divider()
    
    st.header("📌 Modo de Operação")
    modo = st.radio("Escolha a funcionalidade:", [
        "🔍 Análise Individual por Ticker", 
        "⚡ Scanner Ibovespa (Top Blue Chips)"
    ])
    
    st.divider()
    st.info("💡 **Dica:** O Scanner analisa as principais empresas do Ibovespa de forma consolidada.")

# ==========================================
# MODO 1: ANÁLISE INDIVIDUAL POR TICKER
# ==========================================
if modo == "🔍 Análise Individual por Ticker":
    col_input, col_btn = st.columns([3, 1])
    with col_input:
        ticker = st.text_input("Ticker da Ação:", placeholder="Ex: BBAS3").upper()
    with col_btn:
        st.write(" ") 
        st.write(" ")
        btn_analisar = st.button("🚀 Gerar Dashboard", type="primary", use_container_width=True)

    PROMPT_DASHBOARD = """
    Atue como um analista CNPI, gestor de fundos e especialista em valuation na B3.
    Analise profundamente a ação: {TICKER}.

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
    ```
    Estruture o relatório completo em texto formatado em Markdown seguindo os tópicos:
    ### 1. Resumo Executivo
    ### 2. Modelo de Negócio
    ### 3. Qualidade da Empresa
    ### 4. Análise Financeira dos Últimos 5 Anos
    ### 5. Indicadores Fundamentalistas
    ### 6. Vantagens Competitivas (Moat)
    ### 7. Comparação com Concorrentes
    ### 8. Análise de Endividamento
    ### 9. Dividendos
    ### 10. Riscos
    ### 11. Catalisadores
    ### 12. Valuation
    ### 13. Perspectivas para 1, 3 e 5 anos
    ### 14. Score do Investidor
    ### 15. Conclusão
    """

    if btn_analisar:
        if not api_key:
            st.error("⚠️ Por favor, insira sua API Key na barra lateral à esquerda.")
        elif not ticker:
            st.warning("⚠️ Por favor, informe o ticker do ativo.")
        else:
            try:
                with st.spinner(f"🔍 Coletando dados fundamentalistas e calculando valuation para {ticker}..."):
                    client = genai.Client(api_key=api_key)
                    prompt_final = PROMPT_DASHBOARD.format(TICKER=ticker)
                    
                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=prompt_final,
                    )
                    
                    txt_resposta = response.text
                    json_match = re.search(r'```json\s*(\{.*?\})\s*```', txt_resposta, re.DOTALL)
                    
                    if json_match:
                        dados_json = json.loads(json_match.group(1))
                        
                        st.subheader(f"📌 Painel do Ativo: {ticker}")
                        
                        # CARDS DE MÉTRICAS
                        c1, c2, c3, c4, c5 = st.columns(5)
                        c1.metric("Recomendação", dados_json.get("recomendacao", "N/A"))
                        c2.metric("Preço Justo Estimado", f"R$ {dados_json.get('preco_justo', 0):.2f}")
                        c3.metric("Potencial de Alta", f"+{dados_json.get('potencial_alta_pct', 0)}%")
                        c4.metric("Nota Final Score", f"{dados_json.get('nota_final', 0)} / 10")
                        c5.metric("Qualidade Geral", f"{dados_json.get('qualidade', 0)} / 10")
                        
                        st.divider()

                        # GRÁFICO DE RADAR
                        col_grafico, col_resumo = st.columns([1, 1])
                        
                        with col_grafico:
                            st.markdown("### 🕸️ Perfil Fundamentalista (Score 0 a 10)")
                            df_radar = pd.DataFrame({
                                'Métrica': ['Qualidade', 'Valuation', 'Dividendos', 'Crescimento', 'Risco (Inverso)'],
                                'Nota': [
                                    dados_json.get('qualidade', 0),
                                    dados_json.get('valuation', 0),
                                    dados_json.get('dividendos', 0),
                                    dados_json.get('crescimento', 0),
                                    10 - dados_json.get('risco', 0)
                                ]
                            })
                            fig = px.line_polar(df_radar, r='Nota', theta='Métrica', line_close=True, range_r=[0, 10])
                            fig.update_traces(fill='toself', fillcolor='rgba(0, 230, 118, 0.2)', line_color='#00E676')
                            st.plotly_chart(fig, use_container_width=True)
                            
                        with col_resumo:
                            st.markdown("### 📋 Resumo das Notas")
                            df_tabela = pd.DataFrame([dados_json]).T
                            df_tabela.columns = ["Valor"]
                            st.dataframe(df_tabela, use_container_width=True)

                        st.divider()

                    # RELATÓRIO EM ABAS
                    st.subheader("📑 Relatório CNPI Detalhado")
                    tab1, tab2, tab3, tab4 = st.tabs([
                        "📄 Tese & Negócio", 
                        "📊 Valuation & Finanças", 
                        "⚔️ Moat & Concorrentes", 
                        "⚠️ Riscos & Perspectivas"
                    ])
                    
                    txt_limpo = re.sub(r'```json\s*(\{.*?\})\s*```', '', txt_resposta, flags=re.DOTALL)
                    
                    with tab1:
                        st.markdown(txt_limpo)
                    with tab2:
                        st.markdown(txt_limpo)
                    with tab3:
                        st.markdown(txt_limpo)
                    with tab4:
                        st.markdown(txt_limpo)

            except Exception as e:
                st.error(f"Erro ao processar o dashboard: {e}")

# ==========================================
# MODO 2: SCANNER IBOVESPA (TOP BLUE CHIPS)
# ==========================================
elif modo == "⚡ Scanner Ibovespa (Top Blue Chips)":
    st.subheader("⚡ Scanner Consolidado - Principais Ações do Ibovespa")
    st.write("Clique no botão abaixo para que o analista IA avalie o cenário atual das principais referências da B3.")
    
    btn_scanner = st.button("🔍 Executar Scanner Geral", type="primary")
    
    PROMPT_SCANNER = """
    Atue como um analista CNPI sênior. Analise o momento atual de mercado para as seguintes principais ações do Ibovespa: 
    PETR4, VALE3, ITUB4, BBDC4, BBAS3, WEGE3, ABEV3, B3SA3, MGLU3, RENT3.

    Retorne a resposta EXCLUSIVAMENTE em formato de um array JSON contendo objetos com os seguintes campos para cada ação:
    - "Ticker": o ticker da ação
    - "Setor": setor de atuação
    - "Recomendacao": "COMPRA", "MANUTENCAO" ou "VENDA"
    - "Preco_Justo": preço justo estimado em formato numérico (ex: 35.50)
    - "Potencial_Pct": potencial de alta ou baixa em percentual (ex: 15.2)
    - "Nota_Score": nota de 0 a 10 baseada em fundamentos e valuation

    Não inclua nenhum texto adicional fora do bloco JSON. Retorne apenas o bloco markdown json.
    ```json
    [
      {{"Ticker": "PETR4", "Setor": "Petróleo", "Recomendacao": "COMPRA", "Preco_Justo": 42.00, "Potencial_Pct": 18.5, "Nota_Score": 8.5}}
    ]
    ```
    """

    if btn_scanner:
        if not api_key:
            st.error("⚠️ Por favor, insira sua API Key na barra lateral à esquerda.")
        else:
            try:
                with st.spinner("⚡ Varrendo o mercado e cruzando teses fundamentalistas das principais Blue Chips..."):
                    client = genai.Client(api_key=api_key)
                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=PROMPT_SCANNER,
                    )
                    
                    txt_resp = response.text
                    json_match = re.search(r'```json\s*(\[.*?\])\s*```', txt_resp, re.DOTALL)
                    
                    if json_match:
                        lista_dados = json.loads(json_match.group(1))
                        df_scanner = pd.DataFrame(lista_dados)
                        
                        st.success("Scanner concluído com sucesso!")
                        
                        # Exibição em Tabela Estilizada
                        st.dataframe(df_scanner, use_container_width=True)
                        
                        # Gráfico de Potencial de Alta das Top Ações
                        st.markdown("### 📊 Gráfico Comparativo de Potencial de Alta (%)")
                        fig_bar = px.bar(
                            df_scanner, 
                            x='Ticker', 
                            y='Potencial_Pct', 
                            color='Recomendacao',
                            text='Potencial_Pct',
                            color_discrete_map={'COMPRA': '#00E676', 'MANUTENCAO': '#FFC107', 'VENDA': '#FF5252'}
                        )
                        fig_bar.update_traces(texttemplate='%{text}%', textposition='outside')
                        st.plotly_chart(fig_bar, use_container_width=True)
                    else:
                        st.warning("O formato de resposta da IA não retornou o JSON esperado. Tente novamente.")
            except Exception as e:
                st.error(f"Erro ao executar o scanner: {e}")
