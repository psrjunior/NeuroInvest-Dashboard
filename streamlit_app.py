
import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from datetime import datetime, timedelta
import altair as alt

st.set_page_config(page_title="NeuroInvest", layout="wide")
st.title("📊 NeuroInvest — Inteligência Financeira Autônoma")

# Coleta de ações e FIIs
def obter_dados_yfinance(tickers, dias=90):
    fim = datetime.today()
    inicio = fim - timedelta(days=dias)
    df = yf.download(tickers, start=inicio, end=fim)["Close"]
    if df.empty:
        return pd.DataFrame({t: [] for t in tickers})
    return df

# Coleta de altcoins
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
            "Variação (%)": x.get("price_change_percentage_30d_in_currency"),
            "Market Cap (R$)": x.get("market_cap")
        })
    df = pd.DataFrame(altcoins)
    if not df.empty and "Variação (%)" in df.columns:
        df = df.dropna(subset=["Variação (%)"])
        if not df.empty:
            return df.sort_values("Variação (%)", ascending=False).head(5)
    return pd.DataFrame(altcoins).head(5)

# Dados
acoes = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBAS3.SA", "ABEV3.SA"]
fiis = ["MXRF11.SA", "KNRI11.SA", "HGLG11.SA", "BCFF11.SA", "VISC11.SA"]
df_acoes = obter_dados_yfinance(acoes)
df_fiis = obter_dados_yfinance(fiis)
df_alt = obter_altcoins()

# Bloco Altcoins
st.header("🚀 Altcoins com Maior Potencial de Valorização")

if not df_alt.empty:
    col1, col2 = st.columns([1.5, 1])
    with col1:
        st.dataframe(df_alt, use_container_width=True)
    with col2:
        chart = alt.Chart(df_alt).mark_bar().encode(
            x=alt.X("Variação (%):Q", title="Variação 30d (%)"),
            y=alt.Y("Nome:N", sort="-x"),
            color=alt.Color("Variação (%):Q", scale=alt.Scale(scheme="turbo"))
        ).properties(height=280, title="Ranking por Desempenho (%)")
        st.altair_chart(chart, use_container_width=True)
else:
    st.warning("⚠️ As altcoins não puderam ser carregadas. Tente novamente mais tarde.")

# Simulador de Retorno
st.header("💰 Simulador de Retorno de Investimento")
invest = st.number_input("Valor a investir (R$)", min_value=100.0, value=1000.0, step=100.0)
if not df_alt.empty:
    top = df_alt.iloc[0]
    roe = top["Variação (%)"] / 100
    ganho = invest * roe
    st.success(f"Maior ROE estimado: **{top['Nome']} ({top['Ticker']})**")
    st.markdown(f"- **Variação 30d:** `{top['Variação (%)']:.2f}%`")
    st.markdown(f"- **Ganho Estimado:** `R$ {ganho:,.2f}`")
else:
    st.info("A simulação será exibida quando os dados de altcoins estiverem disponíveis.")

# Chat Simples IA
st.header("🤖 Pergunte ao Agente NeuroInvest")
pergunta = st.text_input("Digite sua pergunta sobre investimentos:")

if pergunta:
    pergunta_lower = pergunta.lower()
    st.markdown(f"**Você:** {pergunta}")
    if "melhor" in pergunta_lower or "altcoin" in pergunta_lower:
        st.markdown(f"**NeuroInvest:** A melhor altcoin no momento é **{top['Nome']} ({top['Ticker']})**, com variação de `{top['Variação (%)']:.2f}%` nos últimos 30 dias.")
    elif "investir" in pergunta_lower:
        st.markdown("**NeuroInvest:** Diversifique seus investimentos e considere seu perfil de risco antes de investir em criptoativos.")
    elif "roe" in pergunta_lower or "retorno" in pergunta_lower:
        st.markdown(f"**NeuroInvest:** O retorno estimado de R$ {invest:,.2f} aplicados em **{top['Nome']}** é de **R$ {ganho:,.2f}**.")
    else:
        st.markdown("**NeuroInvest:** Essa é uma excelente pergunta. Em breve trarei análises mais completas baseadas no seu interesse.")

st.caption("🧠 Desenvolvido por NeuroInvest — Análises com dados reais em tempo real.")
