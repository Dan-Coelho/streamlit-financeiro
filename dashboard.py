import streamlit as st
import pandas as pd
from utils.database import carregar_transacoes
from utils.metricas import (
    carregar_metricas,
    carregar_graficos,
    carregar_outras_metricas,
)
from utils.utils import show_filtros, inject_global_css


df = carregar_transacoes()
df_filtro = df.copy()
categoria_receita = st.session_state.dashboard_categoria_receita
categoria_despesa = st.session_state.dashboard_categoria_despesa
subcategoria_selecionada = st.session_state.dashboard_subcategoria_selecionada
data_inicio = st.session_state.dashboard_data_inicio
data_inicio = pd.to_datetime(data_inicio)
data_fim = st.session_state.dashboard_data_fim
data_fim = pd.to_datetime(data_fim)

inject_global_css()

st.set_page_config(layout="wide", initial_sidebar_state="auto")

st.markdown(
    """
    <div style="text-align: center;">
        <h1 style="font-size: 3.5rem; font-weight: 700; background: var(--color-accent-gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            Dashboard Financeiro da IPnovaEusébio
        </h1>
        <p style="font-size: 1.25rem; color: var(--color-text-primary); max-width: 600px; margin: auto;">
            Ferramenta para análise e prestação de contas
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.space("xsmall")

show_filtros(prefixo="dashboard_")

st.space("xsmall")

st.html("""
<style>
[data-testid="stMetric"] {
    background-color: var(--color-bg-secondary); 
    padding: 15px;
    border-radius: 10px;
}
</style>
""")

carregar_metricas()
st.space("xsmall")
carregar_outras_metricas(
    df_filtro,
    data_inicio,
    data_fim,
    categoria_receita,
    categoria_despesa,
    subcategoria_selecionada,
)
st.space("large")
carregar_graficos()
