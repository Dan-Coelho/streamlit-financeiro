import streamlit as st
import pandas as pd
from utils.logger import logger
from utils.utils import inject_global_css
from utils.metricas import metricas_orcamento, grafico_mm_receitas
from utils.database import carregar_transacoes
from src.agent import agent
from src.tools import ProjetoContext
from langchain.messages import HumanMessage


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

with st.container(horizontal_alignment="center", vertical_alignment="center"):
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

    # show_filtros(prefixo='orcamento_')
    metricas_orcamento()
    st.space("medium")
    st.html("""
                <h2 style='text-align: center; color: #080E08; background-color: #C7DE52; padding: 1rem; border-radius: 0.5rem;'>
                    Gráfico de Receitas por dia
                </h2>
            """)
    grafico_mm_receitas()


with st.expander("Agente de Orçamento"):
    # 1. Inicializa o histórico vazio no session_state
    if "mensagens" not in st.session_state:
        st.session_state.mensagens = []

    # Para a memória funcionar, precisamos de um "ID de conversa" (thread_id)
    config_memoria = {"configurable": {"thread_id": "conversa_teste_1"}}

    # Criamos o contexto do usuário atual (Lembra do ToolRuntime da aula passada?)
    contexto_usuario = ProjetoContext(user_name="João", permissao_admin=True)

    # 2. Desenha todas as mensagens antigas na tela
    for msg in st.session_state.mensagens:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 3. Caixa de entrada de texto
    if prompt := st.chat_input("Fale algo com o bot"):
        # Mostra a mensagem do usuário e salva no histórico
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.mensagens.append({"role": "user", "content": prompt})

        # Cria a resposta do bot, mostra e salva no histórico
        resultado = agent.invoke(
            {"messages": [HumanMessage(content=prompt)]},
            config=config_memoria,
            context=contexto_usuario,
        )

        # A resposta final do agente é sempre a última mensagem da lista
        resposta_final = resultado["messages"][-1].content

        with st.chat_message("assistant"):
            st.markdown(resposta_final)

        st.session_state.mensagens.append(
            {"role": "assistant", "content": resposta_final}
        )
