import streamlit as st
import pandas as pd
import time
from datetime import date
from utils.database import (
    buscar_categorias,
    adicionar_transacao,
    buscar_subcategorias,
    adicionar_categoria,
    adicionar_subcategoria,
    carregar_transacoes,
    excluir_transacao,
    atualizar_transacao,
)
from utils.logger import logger


def salvar_e_limpar(data, descricao, valor, recorrente, cat_id, sub_id):
    with st.container():
        if not descricao or not cat_id:
            aviso = st.empty()
            aviso.error("Por favor, preencha a descrição e selecione uma categoria.")
            time.sleep(1)
            aviso.empty()
        else:
            adicionar_transacao(data, descricao, valor, recorrente, cat_id, sub_id)
            st.session_state["descricao"] = ""
            st.session_state["valor"] = 0.01  # Reset para o valor mínimo permitido


def excluir_e_avisar(id_transacao):
    excluir_transacao(id_transacao)
    st.toast(f"Transação {id_transacao} excluída com sucesso!")
    # O rerun acontece automaticamente ao interagir com o botão se não houver prevent default,
    # mas o toast precisa de um tempo ou ser chamado antes da limpeza de estado.


def editar_transacao():
    st.header("📝 Editar Transação")
    df = carregar_transacoes()

    if df.empty:
        st.info("Nenhuma transação encontrada para editar.")
        return

    # Criar uma lista de opções para o selectbox
    df["display"] = df.apply(
        lambda x: (
            f"ID: {x['id']} | {x['data'].strftime('%d/%m/%Y')} | {x['descricao']} | R$ {x['valor']:.2f}"
        ),
        axis=1,
    )

    transacao_escolhida = st.selectbox(
        "Selecione a transação para editar",
        options=df["id"].tolist(),
        format_func=lambda x: df[df["id"] == x]["display"].values[0],
    )

    if transacao_escolhida:
        dados = df[df["id"] == transacao_escolhida].iloc[0]

        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                nova_data = st.date_input("Data", value=dados["data"])
                nova_desc = st.text_input("Descrição", value=dados["descricao"])
            with col2:
                tipo_atual = "Receita" if dados["valor"] > 0 else "Despesa"
                novo_tipo = st.radio(
                    "Tipo",
                    ["Receita", "Despesa"],
                    index=0 if tipo_atual == "Receita" else 1,
                    horizontal=True,
                )
                novo_valor_abs = st.number_input(
                    "Valor (R$)",
                    min_value=0.01,
                    value=abs(float(dados["valor"])),
                    step=0.01,
                )
                valor_final = (
                    novo_valor_abs if novo_tipo == "Receita" else -novo_valor_abs
                )

            nova_recorrente = st.checkbox("Recorrente", value=bool(dados["recorrente"]))

            # Categorias
            categorias = buscar_categorias()
            cat_index = 0
            for i, c in enumerate(categorias):
                if c["nome"] == dados["categoria"]:
                    cat_index = i
                    break

            nova_cat = st.selectbox(
                "Categoria",
                options=categorias,
                index=cat_index,
                format_func=lambda x: x["nome"],
            )

            # Subcategorias
            subs = buscar_subcategorias(nova_cat["id"])
            sub_index = 0
            for i, s in enumerate(subs):
                if s["nome"] == dados["subcategoria"]:
                    sub_index = i
                    break

            nova_sub = st.selectbox(
                "Subcategoria",
                options=subs,
                index=sub_index,
                format_func=lambda x: x["nome"],
            )

            if st.button("Salvar Alterações", type="primary", use_container_width=True):
                atualizar_transacao(
                    transacao_escolhida,
                    nova_data,
                    nova_desc,
                    valor_final,
                    nova_recorrente,
                    nova_cat["id"],
                    nova_sub["id"] if nova_sub else None,
                )
                st.success("Transação atualizada!")
                time.sleep(1)
                st.rerun()


def deletar_transacao():
    st.header("🗑️ Excluir Transação")
    df = carregar_transacoes()

    if df.empty:
        st.info("Nenhuma transação cadastrada.")
        return

    df_display = df.copy()
    df_display["data"] = df_display.index.strftime("%d/%m/%Y")

    df_display["display"] = df_display.apply(
        lambda x: (
            f"ID: {x['id']} | {x['data']} | {x['descricao']} | R$ {x['valor']:.2f}"
        ),
        axis=1,
    )

    id_para_deletar = st.selectbox(
        "Selecione a transação que deseja remover",
        options=df_display["id"].tolist(),
        format_func=lambda x: df_display[df_display["id"] == x]["display"].values[0],
    )

    if id_para_deletar:
        st.warning(
            f"Você tem certeza que deseja excluir a transação ID {id_para_deletar}?"
        )
        if st.button("Confirmar Exclusão", type="primary", use_container_width=True):
            excluir_transacao(id_para_deletar)
            st.success("Transação removida com sucesso!")
            time.sleep(1)
            st.rerun()


def check_login():
    with st.container(horizontal_alignment="center"):
        st.title("Dashboard Financeiro da IPNJ-Eusébio", text_alignment="center")
        st.divider()
        st.warning("Área restrita. Por favor, faça login.", width=300)
        st.button("Log in com Google", on_click=st.login)
        st.stop()  # st.stop() impede que o resto do código rode


def nova_transacao():
    st.header("➕ Nova Transação")

    # Removemos o st.form para permitir que a página recarregue ao mudar a categoria
    data = st.date_input("Data", value=date.today(), key="data")
    descricao = st.text_input(
        "Descrição", placeholder="Ex: Aluguel, Salário, Mercado", key="descricao"
    )

    # Tipo de Transação para definir o sinal do valor
    tipo_op = st.radio("Tipo", ["Receita", "Despesa"], horizontal=True)
    valor_input = st.number_input(
        "Valor (R$)", min_value=0.01, step=0.01, format="%.2f", key="valor"
    )

    # Ajusta o valor baseado no tipo
    valor = valor_input if tipo_op == "Receita" else -valor_input

    recorrente = st.checkbox("É recorrente?")

    # Categorias (Carregadas em tempo real)
    categorias_existentes = buscar_categorias()

    categoria_selecionada = st.selectbox(
        "Categoria",
        options=categorias_existentes,
        format_func=lambda x: x["nome"] if x else "Selecione...",
    )

    # Subcategorias dinâmicas baseadas na categoria selecionada
    subcategorias_existentes = []
    if categoria_selecionada:
        subcategorias_existentes = buscar_subcategorias(categoria_selecionada["id"])

    subcategoria_selecionada = st.selectbox(
        "Subcategoria",
        options=subcategorias_existentes,
        format_func=lambda x: x["nome"] if x else "Nenhuma",
    )
    cat_id = categoria_selecionada["id"]
    sub_id = subcategoria_selecionada["id"] if subcategoria_selecionada else None

    # Botão comum em vez de form_submit_button
    if st.button(
        "Salvar Transação",
        type="primary",
        use_container_width=True,
        on_click=salvar_e_limpar,
        args=(data, descricao, valor, recorrente, cat_id, sub_id),
    ):
        logger.info(f"Salvando transação...{descricao}-{valor}")


def nova_categoria():
    st.header("➕ Gerenciar Categorias")

    with st.form("form_categoria", clear_on_submit=True):
        nome = st.text_input(
            "Nome da Nova Categoria", placeholder="Ex: Moradia, Alimentação, Lazer"
        )
        submit = st.form_submit_button("Cadastrar Categoria")

        if submit:
            if nome:
                if adicionar_categoria(nome):
                    st.success(f"Categoria '{nome}' cadastrada com sucesso!")
                else:
                    st.error(
                        f"Erro ao cadastrar: a categoria '{nome}' já existe ou ocorreu um erro."
                    )
            else:
                st.warning("Por favor, digite um nome para a categoria.")

    st.divider()
    st.subheader("Categorias Existentes")
    categorias = buscar_categorias()
    if categorias:
        for cat in categorias:
            st.write(f"- {cat['nome']}")
    else:
        st.info("Nenhuma categoria cadastrada.")


def nova_subcategoria():
    st.header("➕ Gerenciar Subcategorias")

    categorias = buscar_categorias()

    if not categorias:
        st.warning("Você precisa cadastrar uma categoria antes de criar subcategorias.")
        if st.button("Ir para Nova Categoria"):
            # Aqui poderíamos usar uma lógica de navegação, mas vamos apenas avisar
            st.info("Use o menu lateral para ir em 'Nova Categoria'")
        return

    with st.form("form_subcategoria", clear_on_submit=True):
        categoria_pai = st.selectbox(
            "Selecione a Categoria Pai",
            options=categorias,
            format_func=lambda x: x["nome"],
        )
        nome_sub = st.text_input(
            "Nome da Subcategoria", placeholder="Ex: Aluguel, Supermercado, Restaurante"
        )
        submit = st.form_submit_button("Cadastrar Subcategoria")

        if submit:
            if nome_sub and categoria_pai:
                if adicionar_subcategoria(nome_sub, categoria_pai["id"]):
                    st.success(
                        f"Subcategoria '{nome_sub}' cadastrada em '{categoria_pai['nome']}'!"
                    )
                else:
                    st.error("Erro ao cadastrar subcategoria.")
            else:
                st.warning("Preencha todos os campos.")

    st.divider()
    st.subheader("Subcategorias por Categoria")
    for cat in categorias:
        subs = buscar_subcategorias(cat["id"])
        if subs:
            with st.expander(f"📁 {cat['nome']}"):
                for s in subs:
                    st.write(f"- {s['nome']}")


def show_filtros():
    categorias = buscar_categorias()
    IDS_RECEITA = [7, 8, 9, 10]
    IDS_DESPESA = [1, 2, 3, 4, 5, 6]
    categorias_receita = [c for c in categorias if c["id"] in IDS_RECEITA]
    categorias_despesa = [c for c in categorias if c["id"] in IDS_DESPESA]
    subcategorias = buscar_subcategorias

    with st.expander("Filtros", width="stretch"):
        st.caption("Escolha um período")
        col1, col2 = st.columns(2)
        with col1:
            st.date_input("Data inicial", key="data_inicio")
        with col2:
            st.date_input("Data final", key="data_fim")
        st.caption("Escolha uma categoria")

        col3, col4, col5 = st.columns(3)
        with col3:
            categoria_receita = st.selectbox(
                "Receita",
                options=categorias_receita,
                format_func=lambda x: x["nome"],
                key="categoria_receita",
                index=None,
            )

        with col4:
            categoria_despesa = st.selectbox(
                "Despesa",
                options=categorias_despesa,
                format_func=lambda x: x["nome"],
                key="categoria_despesa",
                index=None,
            )

        with col5:
            cat_receita = st.session_state.get("categoria_receita")
            cat_despesa = st.session_state.get("categoria_despesa")
            if categoria_receita:
                st.selectbox(
                    "Subcategoria",
                    options=subcategorias(cat_receita["id"]),
                    format_func=lambda x: x["nome"],
                    key="subcategoria_selecionada",
                    index=None,
                )
            elif categoria_despesa:
                st.selectbox(
                    "Subcategoria",
                    options=subcategorias(cat_despesa["id"]),
                    format_func=lambda x: x["nome"],
                    key="subcategoria_selecionada",
                    index=None,
                )
            else:
                # ✅ Garante que volta a None quando nenhuma categoria está selecionada
                st.session_state["subcategoria_selecionada"] = None


def inject_global_css():
    """Injects global CSS styles into the Streamlit app."""
    css = """
    <style>
        /* --- Import Google Font --- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        /* --- CSS Variables --- */
        :root {
            --color-bg-primary: #1F1FOF;
            --color-bg-secondary: #080E08;
            --color-bg-tertiary: #4B5030;
            --color-accent-primary: #2060DF;
            --color-accent-secondary: #06132D;
            --color-accent-gradient: linear-gradient(135deg, #2060DF 0%, #A6BFF2 100%);
            --color-text-primary: #E6EDF3;
            --color-text-secondary: #a6b9f2;
            --color-border: #30363D;
            --color-success: #3FB950;
            --color-warning: #D29922;
            --color-error: #F85149;
        }

        /* --- Global Styles --- */
        body {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background-color: var(--color-bg-primary);
        }
        
        /* --- Sidebar Styling --- */
        [data-testid="stSidebar"] {
            background-color: var(--color-bg-secondary);
            border-right: 1px solid var(--color-border);
        }
        
        /* --- Main Content Styling --- */
        .stButton>button {
            border-radius: 8px;
            padding: 0.6rem 1.5rem;
            font-weight: 600;
            transition: opacity 0.2s ease, background-color 0.2s ease;
            border: 1px solid var(--color-accent-primary);
            background-color: transparent;
            color: var(--color-accent-primary);
        }

        .stButton>button:hover {
            background-color: var(--color-bg-tertiary);
        }
        
        /* Primary Button Style */
        .stButton>button[kind="primary"] {
            background: var(--color-accent-gradient);
            color: white;
            border: none;
        }

        .stButton>button[kind="primary"]:hover {
            opacity: 0.9;
            color: white;
        }

        /* Destructive Button Style (for logout) */
         .stButton>button[kind="destructive"] {
            background-color: transparent;
            color: var(--color-error);
            border: 1px solid var(--color-error);
        }
        
        .stButton>button[kind="destructive"]:hover {
            background-color: rgba(248, 81, 73, 0.1);
        }

        /* Form Submit Button */
        div[data-testid="stFormSubmitButton"] > button {
             background: var(--color-accent-gradient);
             color: white;
             border: none;
        }
         div[data-testid="stFormSubmitButton"] > button:hover {
            opacity: 0.9;
         }
        
        /* --- Input & Forms --- */
        .stTextInput input, .stTextArea textarea {
            background-color: var(--color-bg-tertiary);
            border: 1px solid var(--color-border);
            border-radius: 8px;
            color: var(--color-text-primary);
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: var(--color-accent-primary);
            box-shadow: 0 0 0 1px var(--color-accent-primary);
        }

        /* --- Cards --- */
        .card {
            background-color: var(--color-bg-secondary);
            border: 1px solid var(--color-border);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
            transition: border-color 0.3s ease;
            text-decoration: none; /* Remove underline from links */
            color: var(--color-text-primary); /* Default text color */
        }

        .card:hover {
            border-color: var(--color-accent-primary);
        }

        .card h3 {
            margin-top: 0;
            color: var(--color-text-primary);
        }

        .card p {
            color: var(--color-text-secondary);
            font-size: 0.9rem;
        }

        /* --- Chat Messages --- */
        [data-testid="stChatMessage"] {
            background-color: var(--color-bg-secondary);
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 0.5rem;
        }

        [data-testid="stChatMessage"] [data-testid="stChatMessageAvatarAssistant"] {
            background: var(--color-accent-gradient);
        }

        /* User message - right aligned with gradient */
        [data-testid="stChatMessageContent"] {
            color: var(--color-text-primary);
        }

        /* Source citation style */
        .source-citation {
            background-color: var(--color-bg-primary);
            border: 1px solid var(--color-accent-primary);
            border-radius: 8px;
            padding: 0.5rem;
            margin-top: 0.5rem;
            font-size: 0.8rem;
            color: var(--color-text-secondary);
        }

        /* --- Headers --- */
        h1, h2, h3, h4, h5, h6 {
            color: var(--color-text-primary);
        }

        /* --- Links --- */
        a {
            color: var(--color-accent-primary);
            text-decoration: none;
        }

        a:hover {
            color: var(--color-accent-secondary);
        }

        /* --- Radio buttons --- */
        [data-testid="stRadio"] {
            background-color: var(--color-bg-secondary);
            border-radius: 8px;
            padding: 0.5rem;
        }

        /* --- Expander --- */
        [data-testid="stExpander"] {
            background-color: var(--color-bg-secondary);
            border: 1px solid var(--color-border);
            border-radius: 8px;
        }

        /* --- Toast/Messages --- */
        [data-testid="stToast"] {
            background-color: var(--color-bg-tertiary);
            border: 1px solid var(--color-border);
        }

        /* --- Success/Error/Warning messages --- */
        [data-testid="stSuccess"], [data-testid="stError"], [data-testid="stWarning"], [data-testid="stInfo"] {
            border-radius: 8px;
        }

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
