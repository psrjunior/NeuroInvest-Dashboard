
import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="NeuroInvest Dashboard", layout="wide")
st.title("🧠 NeuroInvest - Inteligência Financeira Autônoma")

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
        "order": "market_cap_asc",
        "per_page": 100,
        "page": 1,
        "price_change_percentage": "30d"
    }
    r = requests.get(url, params=params)
    if r.status_code != 200:
        return pd.DataFrame()
    data = r.json()
    altcoins = []
    for x in data:
        if 1e9 < x.get("market_cap", 0) < 3e10:
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
    return pd.DataFrame()

acoes = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBAS3.SA", "ABEV3.SA"]
fiis = ["MXRF11.SA", "KNRI11.SA", "HGLG11.SA", "BCFF11.SA", "VISC11.SA"]

with st.spinner("🔄 Carregando dados reais do mercado..."):
    df_acoes = obter_dados_yfinance(acoes)
    df_fiis = obter_dados_yfinance(fiis)
    df_alt = obter_altcoins()

st.subheader("📊 Desempenho das Ações - Últimos 90 dias")
if not df_acoes.empty:
    st.line_chart(df_acoes)
else:
    st.warning("⚠️ Não foi possível carregar dados das ações agora.")

st.subheader("🏢 Desempenho dos FIIs - Últimos 90 dias")
if not df_fiis.empty:
    st.line_chart(df_fiis)
else:
    st.warning("⚠️ Não foi possível carregar dados dos FIIs agora.")

st.subheader("🚀 Top 5 Altcoins com Maior Potencial de Valorização")
if not df_alt.empty:
    st.dataframe(df_alt, use_container_width=True)
else:
    st.warning("⚠️ Não foi possível carregar os dados das altcoins no momento.")

st.subheader("📥 Exportar relatório")
if st.button("Gerar CSV de ativos"):
    relatorio = pd.concat([df_acoes.iloc[-1:], df_fiis.iloc[-1:]], axis=1)
    st.download_button("📎 Baixar CSV", data=relatorio.to_csv().encode(), file_name="neuroinvest_relatorio.csv", mime="text/csv")

st.markdown("---")
st.caption("Desenvolvido por NeuroInvest - IA Financeira com Dados em Tempo Real")
