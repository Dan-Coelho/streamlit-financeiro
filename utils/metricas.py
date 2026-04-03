from datetime import date
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.logger import logger


categoria_receita = st.session_state.categoria_receita
categoria_despesa = st.session_state.categoria_despesa
subcategoria_selecionada = st.session_state.subcategoria_selecionada
data_inicio = st.session_state.data_inicio
data_inicio = pd.to_datetime(data_inicio)
data_fim = st.session_state.data_fim
data_fim = pd.to_datetime(data_fim)
mes_atual = date.today().month
ano_atual = date.today().year


def carregar_metricas(df):
    receitas = df[df["tipo"] == "Receita"]
    despesas = df[df["tipo"] == "Despesa"]
    data_inicio = st.session_state.data_inicio
    data_inicio = pd.to_datetime(data_inicio)
    data_fim = st.session_state.data_fim
    data_fim = pd.to_datetime(data_fim)
    receitas = receitas[(receitas.index >= data_inicio) & (receitas.index <= data_fim)]
    despesas = despesas[(despesas.index >= data_inicio) & (despesas.index <= data_fim)]
    if df.empty:
        st.info("Nenhuma transação registrada ainda. Use a barra lateral para começar!")
    else:
        # Métricas Rápidas
        receitas_total = receitas["valor"].sum()
        despesas_total = abs(despesas["valor"].sum())
        saldo = receitas_total - despesas_total

        m1, m2, m3 = st.columns(3)
        m1.metric(
            ":blue[TOTAL DE RECEITAS]",
            value=f":green[R$ {receitas_total:,.2f}]".replace(",", "X")
            .replace(".", ",")
            .replace("X", "."),
            delta_color="normal",
            border=True,
        )
        m2.metric(
            ":blue[TOTAL DE DESPESAS]",
            value=f":red[R$ {despesas_total:,.2f}]".replace(",", "X")
            .replace(".", ",")
            .replace("X", "."),
            delta_color="inverse",
            border=True,
        )
        m3.metric(
            ":blue[SALDO ATUAL]",
            value=f"R$ {saldo:,.2f}".replace(",", "X")
            .replace(".", ",")
            .replace("X", "."),
            border=True,
        )


def carregar_metricas_sem_filtro(df):
    despesas = df[df["tipo"] == "Despesa"]
    copia_despesas = despesas.copy()
    # Cálculo das despesas recorrentes no mês anterior
    despesas_recorrentes = copia_despesas[
        (copia_despesas["recorrente"] == 1)
        & (copia_despesas.index.month == mes_atual - 1)
        & (copia_despesas.index.year == ano_atual)
    ]["valor"].sum()
    # Cálculo da maior despesa do mês atual
    maior_despesa = copia_despesas[
        (copia_despesas.index.month == mes_atual)
        & (copia_despesas.index.year == ano_atual)
    ]["valor"].min()
    # Cálculo da média de despesas
    despesas_mensais = copia_despesas.resample("ME")["valor"].sum()
    media_mensal_despesas = abs(despesas_mensais.iloc[:-1]).mean()

    m1, m2, m3 = st.columns(3)
    m1.metric(
        ":blue[DESPESAS RECORRENTES DO MÊS ANTERIOR]",
        f":red[R$ {despesas_recorrentes:,.2f}]".replace(",", "X")
        .replace(".", ",")
        .replace("X", "."),
        delta_color="normal",
    )
    m2.metric(
        ":blue[MÉDIA MENSAL DE DESPESAS]",
        f":red[R$ {media_mensal_despesas:,.2f}]".replace(",", "X")
        .replace(".", ",")
        .replace("X", "."),
        delta_color="normal",
    )
    m3.metric(
        ":blue[MAIOR DESPESA DO MÊS ATUAL]",
        f":red[R$ {maior_despesa:,.2f}]".replace(",", "X")
        .replace(".", ",")
        .replace("X", "."),
        delta_color="inverse",
    )


def carregar_outras_metricas(df):
    receitas = df[df["tipo"] == "Receita"]
    despesas = df[df["tipo"] == "Despesa"]
    data_inicio = st.session_state.data_inicio
    data_inicio = pd.to_datetime(data_inicio)
    data_fim = st.session_state.data_fim
    data_fim = pd.to_datetime(data_fim)
    periodo = data_fim - data_inicio
    receitas = receitas[(receitas.index >= data_inicio) & (receitas.index <= data_fim)]
    despesas = despesas[(despesas.index >= data_inicio) & (despesas.index <= data_fim)]

    if categoria_receita:
        st.markdown(
            """
            Métricas de :green[RECEITAS]
        """,
            text_alignment="center",
        )
        receitas = receitas[
            receitas["categoria"] == st.session_state.categoria_receita["nome"]
        ]
        if st.session_state.subcategoria_selecionada is not None:
            receitas = receitas[
                receitas["subcategoria"]
                == st.session_state.subcategoria_selecionada["nome"]
            ]
            m6, m7, m8 = st.columns(3)
            m6.metric(
                f" Total de :green[{st.session_state.subcategoria_selecionada['nome'].upper()}]",
                f"R$ {receitas['valor'].sum():,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
                delta_color="normal",
            )
            m7.metric(
                f"Média de :green[{st.session_state.subcategoria_selecionada['nome'].upper()}]",
                f"R$ {receitas['valor'].mean():,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
                delta_color="normal",
            )
            m8.metric(
                f"Média diária de :green[{st.session_state.subcategoria_selecionada['nome'].upper()}]",
                f"R$ {receitas['valor'].sum() / periodo.days:,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
                delta_color="normal",
            )
        else:
            m6, m7, m8 = st.columns(3)
            m6.metric(
                f" Total de :green[{st.session_state.categoria_receita['nome'].upper()}]",
                f"R$ {receitas['valor'].sum():,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
                delta_color="normal",
            )
            m7.metric(
                f"Média de :green[{st.session_state.categoria_receita['nome'].upper()}]",
                f"R$ {receitas['valor'].mean():,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
                delta_color="normal",
            )
            m8.metric(
                f"Média diária de :green[{st.session_state.categoria_receita['nome'].upper()}]",
                f"R$ {receitas['valor'].sum() / periodo.days:,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
                delta_color="normal",
            )

    if st.session_state.categoria_despesa:
        st.markdown(
            """
            Métricas de :red[DESPESAS]
        """,
            text_alignment="center",
        )
        despesas = despesas[
            despesas["categoria"] == st.session_state.categoria_despesa["nome"]
        ]
        if st.session_state.subcategoria_selecionada is not None:
            despesas = despesas[
                despesas["subcategoria"]
                == st.session_state.subcategoria_selecionada["nome"]
            ]
            m8, m9, m10 = st.columns(3)
            m8.metric(
                f" Total de :red[{st.session_state.subcategoria_selecionada['nome'].upper()}]",
                f"R$ {despesas['valor'].sum():,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
                delta_color="normal",
            )
            m9.metric(
                f"Média de :red[{st.session_state.subcategoria_selecionada['nome'].upper()}]",
                f"R$ {despesas['valor'].mean():,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
                delta_color="normal",
            )
            m10.metric(
                f"Média diária de :red[{st.session_state.subcategoria_selecionada['nome'].upper()}]",
                f"R$ {despesas['valor'].sum() / periodo.days:,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
                delta_color="normal",
            )
        else:
            m8, m9, m10 = st.columns(3)
            m8.metric(
                f" Total de :red[{st.session_state.categoria_despesa['nome'].upper()}]",
                f"R$ {despesas['valor'].sum():,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
                delta_color="normal",
            )
            m9.metric(
                f"Média de :red[{st.session_state.categoria_despesa['nome'].upper()}]",
                f"R$ {despesas['valor'].mean():,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
                delta_color="normal",
            )
            m10.metric(
                f"Média diária de :red[{st.session_state.categoria_despesa['nome'].upper()}]",
                f"R$ {despesas['valor'].sum() / periodo.days:,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
                delta_color="normal",
            )


def carregar_graficos(df):
    df_copy = df.copy()
    receitas = df[df["valor"] > 0]
    despesas = df[df["valor"] < 0].copy()
    despesas["valor_abs"] = despesas["valor"].abs()
    data_inicio = st.session_state.data_inicio
    data_inicio = pd.to_datetime(data_inicio)
    data_fim = st.session_state.data_fim
    data_fim = pd.to_datetime(data_fim)
    receitas = receitas[(receitas.index >= data_inicio) & (receitas.index <= data_fim)]
    despesas = despesas[(despesas.index >= data_inicio) & (despesas.index <= data_fim)]
    despesas_agrupadas = (
        despesas.groupby("categoria")["valor"].sum().abs().reset_index()
    )
    receitas_agrupadas = receitas.groupby("categoria")["valor"].sum().reset_index()
    periodo = data_fim - data_inicio

    # Gráfico de Saldo
    df_copy = df_copy[(df_copy.index >= data_inicio) & (df_copy.index <= data_fim)]
    saldo_diario = df_copy.groupby(df_copy.index)["valor"].sum()
    saldo_acumulado = saldo_diario.cumsum().reset_index()
    saldo_acumulado.columns = ["data", "saldo"]
    line = px.line(saldo_acumulado, x="data", y="saldo", title="Saldo Acumulado")
    line.update_layout(
        title="Título do Gráfico",
        xaxis_title="Data",
        yaxis_title="Valor (R$)",
        showlegend=True,
        height=400,
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        font=dict(size=12),
        margin=dict(l=40, r=40, t=60, b=40),
    )
    st.plotly_chart(line, use_container_width=True)

    # Gráficos de Categorias
    aba_grafico_receitas, aba_grafico_despesas = st.tabs(["Receitas", "Despesas"])
    with aba_grafico_receitas:
        if not receitas.empty:
            fi = px.pie(
                receitas,
                names=receitas["categoria"],
                values=receitas["valor"],
                color=receitas["categoria"],
            )
            fig = px.bar(
                receitas,
                x=receitas["categoria"],
                y=receitas["valor"],
                color=receitas["categoria"],
            )
            fig.update_layout(
                title="Receitas por Categoria",
                xaxis_title="Categoria",
                yaxis_title="Valor",
                bargap=0.2,
                plot_bgcolor="rgba(0, 0, 0, 0)",
                paper_bgcolor="rgba(0, 0, 0, 0)",
            )
            st.plotly_chart(fi, use_container_width=True)
        else:
            st.info("Nenhuma receita encontrada.")

    with aba_grafico_despesas:
        if not despesas.empty:
            fi = px.pie(
                despesas_agrupadas,
                names="categoria",
                values="valor",
                color="categoria",
                hover_data=["valor"],
            )
            fig = px.bar(
                despesas_agrupadas, x="categoria", y="valor", color="categoria"
            )
            fig.update_layout(
                title="Despesas por Categoria",
                xaxis_title="Categoria",
                yaxis_title="Valor",
                bargap=0.2,
                plot_bgcolor="rgba(0, 0, 0, 0)",
                paper_bgcolor="rgba(0, 0, 0, 0)",
            )
            st.plotly_chart(fi, use_container_width=True)
        else:
            st.info("Nenhuma receita encontrada.")


def calcular_metricas_orcamento(df):
    """
    Calcula as métricas financeiras principais sem renderizar no Streamlit.
    Retorna um dicionário com os valores calculados.
    """
    # df_metricas = carregar_transacoes()
    if df.empty:
        return None

    receitas = df[df["tipo"] == "Receita"]
    copia_receitas = receitas.copy()
    despesas = df[df["tipo"] == "Despesa"]
    copia_despesas = despesas.copy()

    # 1. Cálculo da média mensal de despesas recorrentes
    despesas_recorrentes = despesas[despesas["recorrente"] == 1]
    despesas_recorrentes_por_mes = despesas_recorrentes.resample("ME")["valor"].sum()

    # Pega a média dos meses anteriores (excluindo o atual se possível)
    if len(despesas_recorrentes_por_mes) >= 2:
        media_mensal_despesas_recorrentes = (
            abs(despesas_recorrentes_por_mes).iloc[:-1].mean()
        )
    else:
        media_mensal_despesas_recorrentes = abs(despesas_recorrentes_por_mes).mean()

    # 2. Cálculo da média mensal de receitas
    copia_receitas = copia_receitas.iloc[:-1]
    rec_resampled = copia_receitas.resample("ME")["valor"].sum()
    rec_media_mensal = rec_resampled.mean()

    # 3. Cálculo da Margem de Segurança (mês atual)
    receita_atual = rec_resampled.tail(1).iat[0] if not rec_resampled.empty else 0
    margem_seguranca = (
        ((receita_atual - abs(media_mensal_despesas_recorrentes)) / receita_atual) * 100
        if receita_atual > 0
        else 0
    )

    # 4. Cálculo do Cash Runway
    receitas_total = receitas["valor"].sum()
    despesas_total = copia_despesas["valor"].sum()
    saldo = receitas_total + despesas_total

    despesas_por_mes = copia_despesas.resample("ME")["valor"].sum()
    if len(despesas_por_mes) >= 2:
        media_mensal_despesas = abs(despesas_por_mes).iloc[-4:-1].mean()
    else:
        media_mensal_despesas = abs(despesas_por_mes).mean()

    cash_runway = (
        saldo / abs(media_mensal_despesas) if media_mensal_despesas != 0 else 0
    )

    return {
        "media_mensal_despesas_recorrentes": media_mensal_despesas_recorrentes,
        "rec_media_mensal": rec_media_mensal,
        "margem_seguranca": margem_seguranca,
        "cash_runway": cash_runway,
        "saldo_atual": saldo,
        "media mensal de despesas": media_mensal_despesas,
    }


def metricas_orcamento(df):
    data = calcular_metricas_orcamento(df=df)

    if data is None:
        st.info("Nenhuma transação registrada ainda. Use a barra lateral para começar!")
        return

    m1, m2 = st.columns(2)
    m1.metric(
        ":blue[MÉDIA MENSAL DE DESPESAS RECORRENTES]",
        value=f":red[R$ {data['media_mensal_despesas_recorrentes']:,.2f}]".replace(
            ",", "X"
        )
        .replace(".", ",")
        .replace("X", "."),
        border=True,
        help="Calcula a média de despesas recorrentes em determinado período",
    )
    m2.metric(
        ":blue[MÉDIA MENSAL DE RECEITAS]",
        value=f":green[R$ {data['rec_media_mensal']:,.2f}]".replace(",", "X")
        .replace(".", ",")
        .replace("X", "."),
        border=True,
        help="Calcula a média de receitas mensais em determinado período",
    )

    ms_reference = data["margem_seguranca"] - 10
    cr_reference = data["cash_runway"] - 3

    m3, m4 = st.columns(2)
    m3.metric(
        ":blue[MARGEM DE SEGURANÇA]",
        value=f"{data['margem_seguranca']:,.2f}%".replace(",", "X")
        .replace(".", ",")
        .replace("X", "."),
        delta=f"{ms_reference:,.2f}",
        border=True,
        help="Esta métrica indica o quanto a arrecadação da igreja pode cair antes que ela não consiga mais honrar seus compromissos fixos.",
    )
    m4.metric(
        ":blue[CASH RUNWAY]",
        value=f"{data['cash_runway']:,.2f} meses".replace(",", "X")
        .replace(".", ",")
        .replace("X", "."),
        delta=f"{cr_reference:,.2f}",
        border=True,
        help="Ela calcula por quantos meses a igreja consegue manter suas atividades caso as receitas cessem completamente.",
    )


def budget_metrics():
    """
    Retorna as métricas formatadas para o agente de IA.
    """
    data = calcular_metricas_orcamento()
    if data is None:
        return "Nenhum dado financeiro disponível no momento."

    return f"""
Aqui estão as métricas financeiras atuais da igreja:
- Saldo Atual Total: R$ {data["saldo_atual"]:,.2f}
- Média Mensal de Receitas: R$ {data["rec_media_mensal"]:,.2f}
- Média Mensal de Despesas Recorrentes: R$ {data["media_mensal_despesas_recorrentes"]:,.2f}
- Margem de Segurança: {data["margem_seguranca"]:,.2f}%
- Cash Runway (Reserva Financeira): {data["cash_runway"]:,.2f} meses
- Média Mensal de Despesas: {data["media mensal de despesas"]:,.2f}
"""


def grafico_mm_receitas(df):
    receitas = df[df["tipo"] == "Receita"]
    rec = receitas.copy().iloc[:-1]
    # receita_media_6m = receitas['valor'].rolling(window='180d').mean()
    rec = rec.resample("d").sum()

    fig = go.Figure()
    fig.add_trace(
        go.Bar(x=rec.index, y=rec["valor"], name="Receita", marker_color="green")
    )
    # fig.add_trace(go.Scatter(
    #     x=rec.index,
    #     y=receita_media_6m,
    #     name='Média Móvel',
    #     mode='lines',
    #     line=dict(color='red', width=3)
    # ))
    st.plotly_chart(fig)
