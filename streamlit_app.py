import streamlit as st
import pandas as pd

st.set_page_config(page_title="NeuroInvest Mínimo", layout="wide")
st.title("✅ NeuroInvest - Versão de Teste Mínima")

st.markdown("Essa é uma versão simplificada do painel para testes de funcionamento no Streamlit Cloud.")

try:
    df_acoes = pd.read_csv("dados/dados_estaticos_acoes.csv")
    df_fiis = pd.read_csv("dados/dados_estaticos_fiis.csv")

    st.subheader("📊 Ações Estáticas")
    st.dataframe(df_acoes)

    st.subheader("🏢 FIIs Estáticos")
    st.dataframe(df_fiis)
except Exception as e:
    st.error(f"Erro ao carregar dados estáticos: {e}")