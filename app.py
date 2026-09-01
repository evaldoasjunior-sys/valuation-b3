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
                    
                    padrao_json = r"```json\s*(\{.*?\})\s*
