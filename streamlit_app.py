
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

# Chat IA
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

# Seção extra: Transcrições de Earnings
st.header("🧾 Transcrições de Earnings — Investing.com (via API)")
api_key = st.text_input("Cole sua RapidAPI Key da Investing.com Ultimate API:", type="password")

top_acoes = [{"ticker": "PETR4", "country": "brazil"}, {"ticker": "VALE3", "country": "brazil"},
             {"ticker": "ITUB4", "country": "brazil"}, {"ticker": "BBAS3", "country": "brazil"},
             {"ticker": "ABEV3", "country": "brazil"}]

top_fiis = [{"ticker": "MXRF11", "country": "brazil"}, {"ticker": "KNRI11", "country": "brazil"},
            {"ticker": "HGLG11", "country": "brazil"}, {"ticker": "BCFF11", "country": "brazil"},
            {"ticker": "VISC11", "country": "brazil"}]

top_altcoins = [{"ticker": "BTC", "country": "united states"}, {"ticker": "ETH", "country": "united states"},
                {"ticker": "ADA", "country": "united states"}, {"ticker": "SOL", "country": "united states"},
                {"ticker": "XRP", "country": "united states"}]

def buscar_transcricao(ticker, country, api_key):
    url = "https://investing-com-ultimate-api.p.rapidapi.com/stocks/earnings/transcript"
    headers = {
        "x-rapidapi-host": "investing-com-ultimate-api.p.rapidapi.com",
        "x-rapidapi-key": api_key
    }
    params = {"ticker": ticker, "country": country}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get("transcript", "❌ Nenhuma transcrição encontrada.")
    else:
        return f"❌ Erro na consulta ({response.status_code})"

if api_key and st.button("🔍 Buscar transcrições das Top 5"):
    for grupo, lista in {
        "🏦 Ações": top_acoes,
        "🏢 FIIs": top_fiis,
        "💰 Altcoins": top_altcoins
    }.items():
        st.subheader(grupo)
        for ativo in lista:
            with st.expander(f"📌 {ativo['ticker']} ({ativo['country'].capitalize()})"):
                resultado = buscar_transcricao(ativo["ticker"], ativo["country"], api_key)
                st.text_area("Transcrição:", resultado, height=300)

st.caption("🧠 Desenvolvido por NeuroInvest — Análises com dados reais em tempo real.")
