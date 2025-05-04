
import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from datetime import datetime, timedelta
import altair as alt

st.set_page_config(page_title="NeuroInvest Dashboard", layout="wide")
st.title("🧠 NeuroInvest - Inteligência Financeira Autônoma")

# Funções de coleta
def obter_dados_yfinance(tickers, dias=90):
    fim = datetime.today()
    inicio = fim - timedelta(days=dias)
    df = yf.download(tickers, start=inicio, end=fim)["Close"]
    if df.empty:
        return pd.DataFrame({t: [] for t in tickers})
    return df

def obter_altcoins():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "brl",
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1,
        "price_change_percentage": "30d"
    }
    r = requests.get(url, params=params)
    if r.status_code != 200:
        return pd.DataFrame()
    data = r.json()
    altcoins = []
    for x in data:
        altcoins.append({
            "Nome": x.get("name"),
            "Ticker": x.get("symbol", "").upper(),
            "Preço": x.get("current_price"),
            "Variação 30d (%)": x.get("price_change_percentage_30d_in_currency"),
            "Market Cap": x.get("market_cap")
        })
    df = pd.DataFrame(altcoins)
    if not df.empty and "Variação 30d (%)" in df.columns:
        df = df.dropna(subset=["Variação 30d (%)"])
        if not df.empty:
            return df.sort_values("Variação 30d (%)", ascending=False).head(5)
    return pd.DataFrame(altcoins).head(5)

# Coleta dos dados
acoes = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBAS3.SA", "ABEV3.SA"]
fiis = ["MXRF11.SA", "KNRI11.SA", "HGLG11.SA", "BCFF11.SA", "VISC11.SA"]

with st.spinner("🔄 Carregando dados reais do mercado..."):
    df_acoes = obter_dados_yfinance(acoes)
    df_fiis = obter_dados_yfinance(fiis)
    df_alt = obter_altcoins()

# Seção Altcoins com gráfico em barra
st.subheader("🚀 Top 5 Altcoins com Maior Potencial de Valorização")

if not df_alt.empty:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.dataframe(df_alt, use_container_width=True)

    with col2:
        chart = alt.Chart(df_alt).mark_bar().encode(
            x=alt.X("Variação 30d (%):Q", title="Variação (%)"),
            y=alt.Y("Nome:N", sort="-x", title="Altcoin"),
            color=alt.value("#2c83f2")
        ).properties(height=250)
        st.altair_chart(chart, use_container_width=True)
else:
    st.warning("⚠️ Não foi possível carregar os dados das altcoins no momento.")

# Simulador de recomendação + ROE
st.subheader("💸 Recomendação Inteligente de Investimento")
investimento = st.number_input("Quanto deseja investir (em R$)?", min_value=100.0, value=1000.0, step=100.0)

if not df_alt.empty:
    top = df_alt.iloc[0]
    estimativa_retorno = top["Variação 30d (%)"] / 100
    lucro_estimado = investimento * estimativa_retorno
    st.success(f"🔹 Melhor altcoin: {top['Nome']} ({top['Ticker']})")
    st.markdown(f"**💰 ROE estimado em 30 dias:** `{estimativa_retorno:.2%}`")
    st.markdown(f"**📈 Lucro estimado:** R$ {lucro_estimado:,.2f}")
else:
    st.info("A recomendação será exibida quando os dados das altcoins estiverem disponíveis.")

# Chat IA Simulado
st.subheader("🤖 Chat com o Agente NeuroInvest")
chat_input = st.text_input("Digite sua pergunta:")

if chat_input:
    st.markdown("**Você:** " + chat_input)
    if "melhor" in chat_input.lower():
        st.markdown(f"**NeuroInvest:** Com base nas últimas análises, a altcoin mais promissora é **{top['Nome']}** com potencial de valorização de `{top['Variação 30d (%)']:.2f}%`.")
    elif "investir" in chat_input.lower():
        st.markdown("**NeuroInvest:** Sempre diversifique seus investimentos e analise seu perfil de risco antes de alocar em criptoativos.")
    else:
        st.markdown("**NeuroInvest:** Pergunta registrada! Em breve trarei respostas mais avançadas com base nos dados do mercado.")

st.caption("Desenvolvido por NeuroInvest - IA Financeira com Análises Reais")
