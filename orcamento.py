import streamlit as st
import pandas as pd
from utils.logger import logger
from utils.utils import inject_global_css
from utils.metricas import metricas_orcamento, grafico_mm_receitas
from utils.database import carregar_transacoes


df = carregar_transacoes() 
df_filtro = df.copy()
categoria_receita = st.session_state.orcamento_categoria_receita
categoria_despesa = st.session_state.orcamento_categoria_despesa
subcategoria_selecionada = st.session_state.orcamento_subcategoria_selecionada
data_inicio = st.session_state.orcamento_data_inicio
data_inicio = pd.to_datetime(data_inicio)
data_fim = st.session_state.orcamento_data_fim
data_fim = pd.to_datetime(data_fim)

inject_global_css()

st.set_page_config(layout="wide", initial_sidebar_state="auto")

with st.container(horizontal_alignment='center', vertical_alignment='center'):
    st.markdown(
    """
    <div style="text-align: center;">
        <h1 style="font-size: 3.5rem; font-weight: 700; background: var(--color-accent-gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            Previsão Orçamentária
        </h1>
        <p style="font-size: 1.25rem; color: var(--color-text-primary); max-width: 600px; margin: auto;">
            Ferramenta para previsão de orçamento
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
    st.space("large")

    #show_filtros(prefixo='orcamento_')
    metricas_orcamento()   
    st.space("medium")
    st.html('''
                <h2 style='text-align: center; color: #080E08; background-color: #C7DE52; padding: 1rem; border-radius: 0.5rem;'>
                    Gráfico de Receitas por dia
                </h2>
            ''')
    grafico_mm_receitas()
    