import streamlit as st
from utils.database import carregar_transacoes, excluir_transacao
from utils.utils import inject_global_css

inject_global_css()

st.title("📋 Histórico de Transações")
st.space("large")


def carregar_tabela_de_transações():
    df = carregar_transacoes()
    # Formatação para exibição
    df_display = df.copy()
    df_display["data"] = df_display.index.strftime("%d/%m/%Y")
    df_display["valor_formatado"] = df_display["valor"].apply(lambda x: f"R$ {x:,.2f}")

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

    # Opção para excluir (Exemplo simples)
    with st.expander("🗑️ Excluir Transação"):
        id_para_excluir = st.number_input(
            "ID da Transação para excluir", min_value=1, step=1
        )
        if st.button("Confirmar Exclusão"):
            excluir_transacao(id_para_excluir)
            st.warning(f"Transação {id_para_excluir} excluída.")
            st.rerun()


carregar_tabela_de_transações()
