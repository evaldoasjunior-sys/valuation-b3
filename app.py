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

# Sidebar - Configurações de API Key e Modos
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
    
    st.header("🎯 Modo de Operação")
    modo_operacao = st.radio(
        "Escolha a funcionalidade:",
        ["Análise Individual (Ticker)", "⚡ Scanner Top Ibovespa (Blue Chips)"]
    )
    
    st.divider()
    st.info("💡 **Dica:** O Scanner analisa as principais empresas do Ibovespa de forma unificada em uma única chamada.")

if modo_operacao == "Análise Individual (Ticker)":
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
                    
                    prompt_template = """Atue como um analista CNPI, gestor de fundos e especialista em valuation com foco na Bolsa de Valores brasileira (B3).
Analise profundamente a ação {TICKER}.

DIRETRIZES FUNDAMENTAIS:
1. Baseie-se nos dados financeiros públicos mais recentes disponíveis.
2. Seja objetivo, analítico e evite jargões desnecessários.
3. Utilize estritamente formatação Markdown (tabelas, negritos e listas) para estruturar a resposta.
4. Para o Valuation (DCF), explicite claramente as premissas matemáticas utilizadas (WACC, taxa de crescimento, etc.) para evitar distorções.

Estruture o relatório completo seguindo EXATAMENTE os tópicos abaixo:

# 1. Resumo Executivo
- O que a empresa faz e Setor de atuação
- Tese central de investimento
- Principais vantagens competitivas e Principais riscos
- Recomendação final (Compra Forte, Compra, Manutenção, Venda ou Venda Forte)
- Nota final (0 a 10)

# 2. Modelo de Negócio
- Como a empresa monetiza e principais produtos/serviços
- Principais clientes e Participação de mercado
- Barreiras de entrada
- Dependência de variáveis macroeconômicas (commodities, juros, dólar, regulação)

# 3. Qualidade da Empresa
Avalie Governança corporativa, Histórico da gestão, Alocação de capital e Política de dividendos.
- Atribua notas (0 a 10) para: Governança, Gestão, Eficiência operacional e Alocação de capital.

# 4. Análise Financeira (Últimos 5 Anos)
[Apresente uma Tabela Markdown contendo: Receita, EBITDA, Lucro Líquido, Margem EBITDA, Margem Líquida, FCO, FCL, Capex, Dívida Líquida]
- Explique brevemente as tendências encontradas.

# 5. Indicadores Fundamentalistas
Apresente e interprete os principais múltiplos (P/L, P/VP, EV/EBITDA, ROE, ROIC, Margens, Div. Yield, Dívida/EBITDA).
- Compare os indicadores com a média do setor e principais concorrentes.

# 6. Vantagens Competitivas (Moat)
Avalie a força da Marca, Escala, Custos de troca, Distribuição e Tecnologia. Explique se existe um 'Moat' sustentável.

# 7. Comparação Setorial
[Apresente uma Tabela Markdown comparando a empresa com 2 ou 3 concorrentes nas métricas: Receita, Margem EBITDA, ROE, P/L e EV/EBITDA]
- Indique quem é o líder do setor.

# 8. Análise de Endividamento
Avalie a qualidade da dívida, prazo médio, indexação e capacidade de pagamento.
- Classifique o Risco de Solidez (Muito Baixo, Baixo, Moderado, Alto, Muito Alto).

# 9. Dividendos
Analise o histórico, sustentabilidade (Payout), Yield atual e projeção futura.
- Classifique a qualidade dos dividendos para o longo prazo.

# 10. Mapa de Riscos
Liste e classifique de 1 a 5 (onde 5 é o mais crítico) os riscos: Macroeconômico, Regulatório, Operacional, Concorrencial e Governança.

# 11. Catalisadores (Triggers)
Identifique 3 a 5 eventos prováveis que podem destravar valor para a ação no curto/médio prazo e o impacto esperado.

# 12. Valuation e Precificação
Apresente a modelagem de preço (Múltiplos e Fluxo de Caixa Descontado).
- Explicite as premissas do DCF (WACC estimado e Crescimento na Perpetuidade - g).
- Informe as Faixas de Preço Justo: Pessimista, Base e Otimista.

# 13. Perspectivas para o Longo Prazo
Resuma as estimativas de crescimento e desafios para os próximos 1, 3 e 5 anos.

# 14. Conclusão e Decisão de Investimento
Responda de forma direta:
1. A empresa possui vantagens duradouras?
2. A ação está barata, justa ou cara?
3. Para qual perfil é adequada? (Dividendos, Valor ou Crescimento)
4. Preço Teto sugerido para compra.

Finalize em destaque com:
- RECOMENDAÇÃO FINAL: [Sua Recomendação]
- CONFIANÇA DA ANÁLISE: [X/10]
- MARGEM DE SEGURANÇA ESTIMADA: [X%]

---
INSTRUÇÃO CRÍTICA DE SISTEMA:
No final absoluto da sua resposta, inclua OBRIGATORIAMENTE um bloco de código JSON puro contendo exatamente as chaves abaixo para integração sistêmica. Não adicione nenhum texto após o JSON.

```json
{
  "nota_final": 8.5,
  "qualidade": 8.5,
  "valuation": 9.0,
  "dividendos": 9.5,
  "crescimento": 7.5,
  "risco": 3.0,
  "preco_justo": 36.00,
  "potencial_alta_pct": 33.3,
  "recomendacao": "COMPRA FORTE"
}
```"""
                    
                    prompt_final = prompt_template.replace("{TICKER}", ticker)
                    
                    modelos_disponiveis = ["gemini-3.6-flash", "gemini-2.5-flash", "gemini-1.5-flash"]
                    response = None
                    
                    for modelo in modelos_disponiveis:
                        try:
                            response = client.models.generate_content(
                                model=modelo,
                                contents=prompt_final,
                            )
                            break
                        except Exception as e_model:
                            if "503" in str(e_model) or "UNAVAILABLE" in str(e_model):
                                continue
                            else:
                                raise e_model
                    
                    if not response:
                        raise Exception("Servidores sobrecarregados momentaneamente. Tente novamente em alguns segundos.")

                    txt_resposta = response.text
                    
                    padrao_json = r"```json\s*(\{.*?\})\s*```"
                    json_match = re.search(padrao_json, txt_resposta, re.DOTALL)
                    
                    if json_match:
                        dados_json = json.loads(json_match.group(1))
                        
                        st.subheader(f"📌 Painel do Ativo: {ticker}")
                        
                        rec_texto = str(dados_json.get("recomendacao", "N/A")).upper()
                        if "COMPRA" in rec_texto:
                            cor_rec = "#1E88E5"
                        elif "VENDA" in rec_texto:
                            cor_rec = "#E53935"
                        else:
                            cor_rec = "#FB8C00"

                        c1, c2, c3, c4, c5 = st.columns(5)
                        
                        with c1:
                            st.markdown(f"""
                                <div style="font-size: 0.85rem; color: #666; margin-bottom: 4px;">Recomendação</div>
                                <div style="font-size: 1.3rem; font-weight: bold; color: {cor_rec}; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                                    {rec_texto}
                                </div>
                            """, unsafe_allow_html=True)
                            
                        c2.metric("Preço Justo Estimado", f"R$ {dados_json.get('preco_justo', 0):.2f}")
                        c3.metric("Potencial de Alta", f"+{dados_json.get('potencial_alta_pct', 0)}%")
                        c4.metric("Nota Final Score", f"{dados_json.get('nota_final', 0)} / 10")
                        c5.metric("Qualidade Geral", f"{dados_json.get('qualidade', 0)} / 10")
                        
                        st.divider()

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
                            
                            mapeamento_nomes = {
                                "nota_final": "Nota Final",
                                "qualidade": "Qualidade",
                                "valuation": "Valuation",
                                "dividendos": "Dividendos",
                                "crescimento": "Crescimento",
                                "risco": "Risco",
                                "preco_justo": "Preço Justo",
                                "potencial_alta_pct": "Potencial de Alta",
                                "recomendacao": "Recomendação"
                            }

                            dados_formatados = {}
                            for chave, valor in dados_json.items():
                                nome_amigavel = mapeamento_nomes.get(chave, chave)
                                if chave == "preco_justo" and isinstance(valor, (int, float)):
                                    dados_formatados[nome_amigavel] = f"R$ {valor:.2f}"
                                elif chave == "potencial_alta_pct" and isinstance(valor, (int, float)):
                                    dados_formatados[nome_amigavel] = f"{valor:.1f}%"
                                else:
                                    dados_formatados[nome_amigavel] = str(valor)

                            df_tabela = pd.DataFrame(list(dados_formatados.items()), columns=["Indicador", "Valor"])
                            st.dataframe(df_tabela, use_container_width=True, hide_index=True)

                        st.divider()

                    st.subheader("📑 Relatório CNPI Detalhado")
                    txt_limpo = re.sub(padrao_json, "", txt_resposta, flags=re.DOTALL)
                    st.markdown(txt_limpo)

            except Exception as e:
                st.error(f"Erro ao processar o dashboard: {e}")

else:
    st.subheader("⚡ Scanner Ibovespa - Principais Blue Chips")
    st.write("Análise consolidada das principais ações de maior peso do Ibovespa gerada por IA.")
    
    if st.button("🚀 Executar Scanner de Oportunidades", type="primary"):
        if not api_key:
            st.error("⚠️ Por favor, insira sua API Key na barra lateral à esquerda ou configure nos Secrets.")
        else:
            try:
                with st.spinner("Analisando as principais blue chips do Ibovespa em lote..."):
                    client = genai.Client(api_key=api_key)
                    
                    prompt_scanner = """Atue como um analista CNPI sênior e especialista em valuation na B3.
Analise as seguintes 10 principais blue chips do Ibovespa: PETR4, VALE3, ITUB4, BBDC4, BBAS3, WEGE3, RENT3, JBSS3, SUZB3, ABEV3.

Retorne APENAS um bloco de código JSON puro contendo um array de objetos. Cada objeto deve conter exatamente estas chaves:
- "ticker": string (ex: "PETR4")
- "empresa": string (nome da empresa)
- "setor": string
- "recomendacao": string ("COMPRA FORTE", "COMPRA", "MANUTENCAO", "VENDA", ou "VENDA FORTE")
- "nota_final": float (0 a 10)
- "potencial_alta_pct": float (ex: 25.5)

Não inclua nenhum texto explicativo antes ou depois do JSON. Apenas o bloco json puro.
```json
[
  {
    "ticker": "PETR4",
    "empresa": "Petrobras",
    "setor": "Petróleo e Gás",
    "recomendacao": "COMPRA",
    "nota_final": 8.5,
    "potencial_alta_pct": 22.0
  }
]
```"""
                    
                    modelos_disponiveis = ["gemini-3.6-flash", "gemini-2.5-flash", "gemini-1.5-flash"]
                    response = None
                    
                    for modelo in modelos_disponiveis:
                        try:
                            response = client.models.generate_content(
                                model=modelo,
                                contents=prompt_scanner,
                            )
                            break
                        except Exception:
                            continue
                            
                    if response:
                        match_arr = re.search(r'```json\s*(\[.*?\])\s*```', response.text, re.DOTALL)
                        if match_arr:
                            lista_acoes = json.loads(match_arr.group(1))
                            df_scanner = pd.DataFrame(lista_acoes)
                            
                            df_scanner = df_scanner.rename(columns={
                                "ticker": "Ticker",
                                "empresa": "Empresa",
                                "setor": "Setor",
                                "recomendacao": "Recomendação",
                                "nota_final": "Nota Final",
                                "potencial_alta_pct": "Potencial de Alta (%)"
                            })
                            
                            def color_recommendation(val):
                                val_upper = str(val).upper()
                                if "COMPRA" in val_upper:
                                    return 'color: #1E88E5; font-weight: bold;'
                                elif "VENDA" in val_upper:
                                    return 'color: #E53935; font-weight: bold;'
                                return 'color: #FB8C00; font-weight: bold;'
                            
                            df_styled = df_scanner.style.map(color_recommendation, subset=['Recomendação'])
                            
                            st.success("Scanner concluído com sucesso!")
                            st.dataframe(df_styled, use_container_width=True, hide_index=True)
                        else:
                            st.error("Erro ao interpretar o formato de resposta da IA.")
                    else:
                        st.error("Erro ao conectar com a API do Gemini.")
            except Exception as e:
                st.error(f"Erro no scanner: {e}")
