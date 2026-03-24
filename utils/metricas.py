from datetime import date
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.database import carregar_transacoes
from utils.logger import logger

df = carregar_transacoes()
df_filtro = df.copy()
categoria_receita = st.session_state.dashboard_categoria_receita
categoria_despesa = st.session_state.dashboard_categoria_despesa
subcategoria_selecionada = st.session_state.dashboard_subcategoria_selecionada
data_inicio = st.session_state.dashboard_data_inicio
data_inicio = pd.to_datetime(data_inicio)
data_fim = st.session_state.dashboard_data_fim
data_fim = pd.to_datetime(data_fim)
mes_atual = date.today().month
ano_atual = date.today().year


def carregar_metricas():
    receitas = df[df["tipo"] == 'Receita']
    despesas = df[df["tipo"] == 'Despesa']
    receitas = receitas[
        (receitas.index >= data_inicio) & (receitas.index <= data_fim)
    ]
    despesas = despesas[
        (despesas.index >= data_inicio) & (despesas.index <= data_fim)
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


def carregar_outras_metricas(df_filtro, data_inicio, data_fim, categoria_receita, categoria_despesa, subcategoria_selecionada=None):
    receitas = df_filtro[df_filtro["tipo"] == 'Receita']
    despesas = df_filtro[df_filtro["tipo"] == 'Despesa']
    receitas = receitas[
        (receitas.index >= data_inicio) & (receitas.index <= data_fim)
    ]
    despesas = despesas[
        (despesas.index >= data_inicio) & (despesas.index <= data_fim)
    ]
    periodo = data_fim - data_inicio
    
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
        (receitas.index >= data_inicio) & (receitas.index <= data_fim)
    ]
    despesas = despesas[
        (despesas.index >= data_inicio) & (despesas.index <= data_fim)
    ]
    despesas_agrupadas = (
        despesas.groupby("categoria")["valor"].sum().abs().reset_index()
    )
    receitas_agrupadas = receitas.groupby("categoria")["valor"].sum().reset_index()
    periodo = data_fim - data_inicio

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


def metricas_orcamento():
        receitas = df[df['tipo'] == 'Receita']
        copia_receitas = receitas.copy()
        despesas = df[df['tipo'] == 'Despesa']
        copia_despesas = despesas.copy()
        
        if df.empty:
            st.info("Nenhuma transação registrada ainda. Use a barra lateral para começar!")
        else:
            # Métricas de Orçamento
            
            # 1. Cálculo da média mensal de despesas recorrentes
            despesas = despesas[despesas['recorrente'] == 1]
            despesas_recorrentes_por_mes = despesas.resample('ME')['valor'].sum()
            media_mensal_despesas_recorrentes = abs(despesas_recorrentes_por_mes).iloc[-4:-1].mean()
            # 2. Cálculo da média mensal de receitas
            copia_receitas = copia_receitas.iloc[:-1]
            copia_receitas = copia_receitas.resample('ME')
            rec_media_mensal = copia_receitas['valor'].sum().mean()
            # 3. Cálculo da Margem de Segurança (mês atual)
            receita_atual = copia_receitas['valor'].sum().tail(1).iat[0]
            margem_seguranca = ((receita_atual - abs(media_mensal_despesas_recorrentes)) / receita_atual) * 100
            ms_reference = margem_seguranca - 10
            # 4. Cálculo do Cash Runway
            receitas_total = receitas["valor"].sum()
            despesas_total = copia_despesas["valor"].sum()
            saldo = receitas_total + despesas_total
            despesas_por_mes = copia_despesas.resample('ME')['valor'].sum()
            media_mensal_despesas = despesas_por_mes.iloc[-4:-1].mean()
            cash_runway = saldo / abs(media_mensal_despesas)
            cr_reference = cash_runway - 3
            # receita_atual = rec['valor'].agg(['sum', 'count', 'mean'])
            # fixo_atual = des['valor'].agg(['sum', 'count', 'mean'])
            # margem_seguranca = (receita_atual['sum'] - fixo_atual['sum']) / receita_atual['sum']
            # receita_media_6m = rec['valor'].rolling(window='180d').mean()
            # st.write(receita_media_6m)
            # receitas_total = receitas["valor"].sum()
            # despesas_total = despesas["valor"].sum()
            # saldo = receitas_total + despesas_total
            # line = px.line(receita_media_6m, title="Receita Média")
            # line.update_layout(
            #     title="Título do Gráfico",
            #     xaxis_title="Data",
            #     yaxis_title="Valor (R$)",
            #     showlegend=True,
            #     height=400,
            #     plot_bgcolor="rgba(0, 0, 0, 0)",
            #     paper_bgcolor="rgba(0, 0, 0, 0)",
            #     font=dict(size=12),
            #     margin=dict(l=40, r=40, t=60, b=40),
            # )
            #st.plotly_chart(line, use_container_width=True)
            m1, m2 = st.columns(2)
            m1.metric(
                ":orange[MÉDIA MENSAL DE DESPESAS RECORRENTES]",
                value=f":red[R$ {media_mensal_despesas_recorrentes:,.2f}]".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
                delta_color="normal",
                border=True,
                help='Calcula a média de despesas recorrentes em determinado período'
            )
            m2.metric(
                ":orange[MÉDIA MENSAL DE RECEITAS]",
                value=f":green[R$ {rec_media_mensal:,.2f}]".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
                delta_color="normal",
                border=True,
                help='Calcula a média de receitas mensais em determinado período'
            )
            m3, m4 = st.columns(2)
            m3.metric(
                ":orange[MARGEM DE SEGURANÇA]",
                value=f":green[{margem_seguranca:,.2f}%]".replace(",", "X")
                .replace(".", ",")
                .replace("X", ".") if margem_seguranca > 0 else f":red[{margem_seguranca:,.2f}%]".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
                delta=f'{ms_reference:,.2f}',
                border=True,
                help='Esta métrica indica o quanto a arrecadação da igreja pode cair antes que ela não consiga mais honrar seus compromissos fixos (salários pastorais, aluguel, energia, manutenção). Para uma igreja, o Ponto de Equilíbrio (Break-even) é o somatório exato das despesas fixas.'
            )
            m4.metric(
                ":orange[CASH RUNWAY]",
                value=f":green[R$ {cash_runway:,.2f}]".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
                delta=f'{cr_reference:,.2f}',
                delta_color="normal",
                border=True,
                help='Ela calcula por quantos meses a igreja consegue manter suas atividades caso as receitas cessem completamente, utilizando apenas o fundo de reserva.'
            )

def grafico_mm_receitas():
    receitas = df[df['tipo'] == 'Receita']
    rec = receitas.copy().iloc[:-1]
    # receita_media_6m = receitas['valor'].rolling(window='180d').mean()
    rec = rec.resample('d').sum()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=rec.index,
        y=rec['valor'],
        name='Receita',
        marker_color='green'
    ))
    # fig.add_trace(go.Scatter(
    #     x=rec.index,
    #     y=receita_media_6m,
    #     name='Média Móvel',
    #     mode='lines',
    #     line=dict(color='red', width=3)
    # ))
    st.plotly_chart(fig)
    