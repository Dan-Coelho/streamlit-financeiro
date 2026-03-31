import streamlit as st
import pandas as pd
from utils.database import carregar_transacoes, excluir_transacao
from utils.utils import inject_global_css
from utils.logger import logger

inject_global_css()

st.title("📋 Histórico de Transações")
st.space("large")


def carregar_tabela_de_transações():
    df = carregar_transacoes()
    # Formatação para exibição
    df_display = df.copy()
    df_display["data"] = df_display.index.strftime("%d/%m/%Y")
    df_display["valor_formatado"] = df_display["valor"].apply(lambda x: f"R$ {x:,.2f}")
    # logger.debug(f"Tabela de transações carregada: {df_display.head()}")
    # Widget de edição/visualização
    # Usando o novo st.data_editor para permitir exclusão
    st.dataframe(
        df_display[
            [
                "id",
                "data",
                "descricao",
                "categoria",
                "subcategoria",
                "valor_formatado",
                "tipo",
                "recorrente",
            ]
        ],
        use_container_width=True,
        hide_index=True,
        width="stretch",
    )


carregar_tabela_de_transações()
