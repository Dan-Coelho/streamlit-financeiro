import streamlit as st
from utils.database import carregar_transacoes
from utils.metricas import (
    carregar_metricas,
    carregar_graficos,
    carregar_outras_metricas,
    carregar_metricas_sem_filtro,
    data_inicio,
    data_fim,
    categoria_receita,
    categoria_despesa,
    subcategoria_selecionada,
)
from utils.utils import show_filtros, inject_global_css


# Carregar o dataframe
df = carregar_transacoes()
df_filtro = df.copy()

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
st.space("medium")

st.markdown(
    """
    <div style="text-align: center;">
        <h1 style="font-size: 1.5rem; font-weight: 700; color: var(--color-text-secondary);">
            Métricas de Despesas
        </h1>
    </div>
""",
    unsafe_allow_html=True,
)


carregar_metricas_sem_filtro(df=df)
st.divider()
st.space("medium")


st.markdown(
    """
    <div style="text-align: center;">
        <h1 style="font-size: 1.5rem; font-weight: 700; color: var(--color-text-secondary);">
            Use o filtro para outras métricas
        </h1>
    </div>
""",
    unsafe_allow_html=True,
)
show_filtros()

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

carregar_metricas(df=df)
st.space("xsmall")
carregar_outras_metricas(df=df)
st.divider()
st.space("medium")
carregar_graficos(df=df)
