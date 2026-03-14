import streamlit as st
from datetime import date
import pandas as pd
import plotly.express as px
from utils.database import carregar_transacoes
from utils.utils import show_filtros, inject_global_css

inject_global_css()
st.set_page_config(layout="wide", initial_sidebar_state="auto")
# st.title('Dashboard Financeiro')
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

df = carregar_transacoes()
df_filtro = df.copy()
categoria_receita = st.session_state.categoria_receita
categoria_despesa = st.session_state.categoria_despesa
categoria_selecionada = bool(categoria_receita or categoria_despesa)
subcategoria_selecionada = st.session_state.subcategoria_selecionada
data_inicial = st.session_state.data_inicio
data_inicial = pd.to_datetime(data_inicial)
data_final = st.session_state.data_fim
data_final = pd.to_datetime(data_final)
mes_atual = date.today().month
ano_atual = date.today().year


def carregar_metricas():
    receitas = df[df["valor"] > 0]
    despesas = df[df["valor"] < 0]
    receitas = receitas[
        (receitas.index >= data_inicial) & (receitas.index <= data_final)
    ]
    despesas = despesas[
        (despesas.index >= data_inicial) & (despesas.index <= data_final)
    ]
    if df.empty:
        st.info("Nenhuma transação registrada ainda. Use a barra lateral para começar!")
    else:
        # Métricas Rápidas
        receitas_total = receitas["valor"].sum()
        despesas_total = despesas["valor"].sum()
        saldo = receitas_total + despesas_total

        m1, m2, m3 = st.columns(3)
        m1.metric(
            ":green[TOTAL DE RECEITAS]",
            value=f":green[R$ {receitas_total:,.2f}]".replace(",", "X")
            .replace(".", ",")
            .replace("X", "."),
            delta_color="normal",
            border=True,
        )
        m2.metric(
            ":red[TOTAL DE DESPESAS]",
            value=f":red[R$ {despesas_total:,.2f}]".replace(",", "X")
            .replace(".", ",")
            .replace("X", "."),
            delta_color="inverse",
            border=True,
        )
        m3.metric(
            "SALDO ATUAL",
            value=f"R$ {saldo:,.2f}".replace(",", "X")
            .replace(".", ",")
            .replace("X", "."),
            border=True,
        )

        despesas_recorrentes = df[
            (df["valor"] < 0)
            & (df["recorrente"] == 1)
            & (df.index.month == mes_atual - 1)
            & (df.index.year == ano_atual)
        ]["valor"].sum()
        maior_despesa = df[
            (df["valor"] < 0)
            & (df.index.month == mes_atual)
            & (df.index.year == ano_atual)
        ]["valor"].min()

        m4, m5 = st.columns(2)
        m4.metric(
            "DESPESAS RECORRENTES DO MÊS ANTERIOR",
            f"R$ {despesas_recorrentes:,.2f}".replace(",", "X")
            .replace(".", ",")
            .replace("X", "."),
            delta_color="normal",
        )
        m5.metric(
            "MAIOR DESPESA DO MÊS ATUAL",
            f"R$ {maior_despesa:,.2f}".replace(",", "X")
            .replace(".", ",")
            .replace("X", "."),
            delta_color="inverse",
        )


def carregar_outras_metricas():
    receitas = df_filtro[df_filtro["valor"] > 0]
    despesas = df_filtro[df_filtro["valor"] < 0]
    receitas = receitas[
        (receitas.index >= data_inicial) & (receitas.index <= data_final)
    ]
    despesas = despesas[
        (despesas.index >= data_inicial) & (despesas.index <= data_final)
    ]
    periodo = data_final - data_inicial

    if categoria_receita:
        st.markdown(
            """
            Métricas de :green[RECEITAS]
        """,
            text_alignment="center",
        )
        receitas = receitas[receitas["categoria"] == categoria_receita["nome"]]
        if subcategoria_selecionada is not None:
            receitas = receitas[
                receitas["subcategoria"] == subcategoria_selecionada["nome"]
            ]
            m6, m7, m8 = st.columns(3)
            m6.metric(
                f" Total de {subcategoria_selecionada['nome']}",
                f"R$ {receitas['valor'].sum():,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
                delta_color="normal",
            )
            m7.metric(
                f"Média de {subcategoria_selecionada['nome']}",
                f"R$ {receitas['valor'].mean():,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
                delta_color="normal",
            )
            m8.metric(
                f"Média diária de {subcategoria_selecionada['nome']}",
                f"R$ {receitas['valor'].sum() / periodo.days:,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
                delta_color="normal",
            )
        else:
            m6, m7, m8 = st.columns(3)
            m6.metric(
                f" Total de {categoria_receita['nome']}",
                f"R$ {receitas['valor'].sum():,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
                delta_color="normal",
            )
            m7.metric(
                f"Média de {categoria_receita['nome']}",
                f"R$ {receitas['valor'].mean():,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
                delta_color="normal",
            )
            m8.metric(
                f"Média diária de {categoria_receita['nome']}",
                f"R$ {receitas['valor'].sum() / periodo.days:,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
                delta_color="normal",
            )

    if categoria_despesa:
        st.markdown(
            """
            Métricas de :red[DESPESAS]
        """,
            text_alignment="center",
        )
        despesas = despesas[despesas["categoria"] == categoria_despesa["nome"]]
        if subcategoria_selecionada is not None:
            despesas = despesas[
                despesas["subcategoria"] == subcategoria_selecionada["nome"]
            ]
            m8, m9, m10 = st.columns(3)
            m8.metric(
                f" Total de {subcategoria_selecionada['nome']}",
                f"R$ {despesas['valor'].sum():,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
                delta_color="normal",
            )
            m9.metric(
                f"Média de {subcategoria_selecionada['nome']}",
                f"R$ {despesas['valor'].mean():,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
                delta_color="normal",
            )
            m10.metric(
                f"Média diária de {subcategoria_selecionada['nome']}",
                f"R$ {despesas['valor'].sum() / periodo.days:,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
                delta_color="normal",
            )
        else:
            m8, m9, m10 = st.columns(3)
            m8.metric(
                f" Total de {categoria_despesa['nome']}",
                f"R$ {despesas['valor'].sum():,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
                delta_color="normal",
            )
            m9.metric(
                f"Média de {categoria_despesa['nome']}",
                f"R$ {despesas['valor'].mean():,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
                delta_color="normal",
            )
            m10.metric(
                f"Média diária de {categoria_despesa['nome']}",
                f"R$ {despesas['valor'].sum() / periodo.days:,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
                delta_color="normal",
            )


def carregar_graficos():
    receitas = df_filtro[df_filtro["valor"] > 0]
    despesas = df_filtro[df_filtro["valor"] < 0].copy()
    despesas["valor_abs"] = despesas["valor"].abs()
    receitas = receitas[
        (receitas.index >= data_inicial) & (receitas.index <= data_final)
    ]
    despesas = despesas[
        (despesas.index >= data_inicial) & (despesas.index <= data_final)
    ]
    despesas_agrupadas = (
        despesas.groupby("categoria")["valor"].sum().abs().reset_index()
    )
    receitas_agrupadas = receitas.groupby("categoria")["valor"].sum().reset_index()
    periodo = data_final - data_inicial

    # Gráfico de Saldo
    saldo_diario = df_filtro.groupby(df_filtro.index)["valor"].sum()
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
                despesas_agrupadas, names="categoria", values="valor", color="categoria"
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
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhuma receita encontrada.")


carregar_metricas()
st.divider()
carregar_outras_metricas()
st.divider()
carregar_graficos()
