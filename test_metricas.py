from datetime import date

import streamlit as st

st.session_state.data_inicio = date(2026, 5, 1)
st.session_state.data_fim = date(2026, 8, 31)
st.session_state.categoria_receita = None
st.session_state.categoria_despesa = None
st.session_state.subcategoria_selecionada = None

from utils.metricas import _dias_no_periodo  # noqa: E402


def test_dias_no_periodo_inclui_data_inicial_e_final():
    """Conta todos os dias, incluindo as duas datas escolhidas pelo usuário."""
    assert _dias_no_periodo(date(2026, 5, 1), date(2026, 8, 31)) == 123
