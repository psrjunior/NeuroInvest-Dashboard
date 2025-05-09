
import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from datetime import datetime, timedelta
import altair as alt

st.set_page_config(page_title="NeuroInvest", layout="wide")
st.title("📊 NeuroInvest — Inteligência Financeira Autônoma")

# Coleta dos dados históricos de ações e FIIs
def obter_dados_yfinance(tickers, dias=90):
    fim = datetime.today()
    inicio = fim - timedelta(days=dias)
    df = yf.download(tickers, start=inicio, end=fim)["Close"]
    return df

def calcular_rentabilidade(df):
    if df.empty:
        return pd.DataFrame()
    retorno = ((df.iloc[-1] - df.iloc[0]) / df.iloc[0]) * 100
    return retorno.reset_index().rename(columns={0: "Variação (%)", "index": "Ticker"})

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
        return df.sort_values("Variação (%)", ascending=False).head(5)
    return pd.DataFrame(altcoins).head(5)

acoes = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBAS3.SA", "ABEV3.SA"]
fiis = ["MXRF11.SA", "KNRI11.SA", "HGLG11.SA", "BCFF11.SA", "VISC11.SA"]

with st.spinner("🔄 Carregando dados reais..."):
    df_acoes_hist = obter_dados_yfinance(acoes)
    df_fiis_hist = obter_dados_yfinance(fiis)
    df_alt = obter_altcoins()

# Ações e FIIs - Ranking de desempenho
st.header("📈 Ranking de Ações e FIIs por Desempenho nos Últimos 90 Dias")

col1, col2 = st.columns(2)
with col1:
    st.subheader("🏦 Ações")
    df_acoes_var = calcular_rentabilidade(df_acoes_hist)
    if not df_acoes_var.empty:
        st.dataframe(df_acoes_var.sort_values("Variação (%)", ascending=False), use_container_width=True)
        chart = alt.Chart(df_acoes_var).mark_bar().encode(
            x=alt.X("Variação (%):Q"),
            y=alt.Y("Ticker:N", sort="-x"),
            color=alt.value("#1f77b4")
        ).properties(height=250)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("Não foi possível carregar dados das ações.")

with col2:
    st.subheader("🏢 FIIs")
    df_fiis_var = calcular_rentabilidade(df_fiis_hist)
    if not df_fiis_var.empty:
        st.dataframe(df_fiis_var.sort_values("Variação (%)", ascending=False), use_container_width=True)
        chart = alt.Chart(df_fiis_var).mark_bar().encode(
            x=alt.X("Variação (%):Q"),
            y=alt.Y("Ticker:N", sort="-x"),
            color=alt.value("#ff7f0e")
        ).properties(height=250)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("Não foi possível carregar dados dos FIIs.")

# Altcoins
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
    st.success(f"Maior ROE estimado: {top['Nome']} ({top['Ticker']})")
    st.markdown(f"- Variação 30d: `{top['Variação (%)']:.2f}%`")
    st.markdown(f"- Ganho Estimado: `R$ {ganho:,.2f}`")

# Consulta Ações Nacionais via Brapi
st.header("🇧🇷 Ações da B3 — Dados Reais com API Brapi.dev")

tickers_b3 = ["PETR4", "VALE3", "ITUB4", "BBAS3", "ABEV3", "WEGE3", "B3SA3", "ELET3", "JBSS3", "LREN3"]
ticker = st.selectbox("Escolha uma ação da B3:", tickers_b3, key="b3_ticker")

@st.cache_data
def buscar_acao_brapi(ticker):
    url = f"https://brapi.dev/api/quote/{ticker}?range=1mo&interval=1d&token=nBHcGESWX8DM6UbfXH1FoF"
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    else:
        return None

dados = buscar_acao_brapi(ticker)

if dados and "results" in dados:
    acao = dados["results"][0]
    st.subheader(f"📈 {acao['longName']} ({acao['symbol']})")
    st.markdown(f"**Preço atual:** R$ {acao['regularMarketPrice']}")
    st.markdown(f"**Variação diária:** {acao['regularMarketChangePercent']:.2f}%")
    st.markdown(f"**Máxima 1M:** R$ {acao['fiftyTwoWeekHigh']}")
    st.markdown(f"**Mínima 1M:** R$ {acao['fiftyTwoWeekLow']}")

    historico = acao.get("historicalDataPrice", [])
    if historico:
        df_hist = pd.DataFrame(historico)
        df_hist["date"] = pd.to_datetime(df_hist["date"], unit="s")
        df_hist["close"] = df_hist["close"].astype(float)
        chart = alt.Chart(df_hist).mark_line().encode(
            x="date:T", y="close:Q"
        ).properties(title=f"Evolução do preço - {ticker}", height=300)
        st.altair_chart(chart, use_container_width=True)
else:
    st.warning("❌ Não foi possível obter os dados da Brapi.")
