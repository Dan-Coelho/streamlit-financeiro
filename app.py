import streamlit as st
from datetime import date
from utils.logger import logger
from utils.utils import (
    check_login,
    nova_transacao,
    nova_categoria,
    nova_subcategoria,
    deletar_transacao,
    inject_global_css,
)


inject_global_css()

emails_autorizados = st.secrets["emails_autorizados"]
email_adm = st.secrets["email_adm"]

# Verifica se o usuário NÃO está logado
if not st.user.is_logged_in:
    check_login()
    logger.info(f"Usuário {st.user.email} logado")


if st.user.email not in emails_autorizados:
    st.error("Você não tem permissão para acessar estes dados.")
    st.button("Sair", on_click=st.logout)
    logger.info(f"Usuário {st.user.email} não autorizado")
    st.stop()

# Iniciar session_state
defaults = {
    "data_inicio": date(2025, 1, 1),
    "data_fim": date.today(),
    "subcategoria_selecionada": None,
    "categoria_receita": None,
    "categoria_despesa": None,
    # adicione outras chaves aqui
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Configuração da Página
st.set_page_config(
    page_title="Dashboard Financeiro Pessoal", page_icon="💰", layout="wide"
)


st.sidebar.image("static/logoescurosemfundo.png", width="content")

with st.sidebar:
    st.html(
        f"<h4 style='text-align: center; color: orange'>Bem-vindo, {st.user.name}! 🎈</h4>"
    )
    # st.write(st.user) # Mostra todos os dados do usuário (email, foto, etc)
    st.button("Sair", on_click=st.logout, width="stretch")


# 2. Definição das páginas
p1 = st.Page("dashboard.py", title="Painel Principal", icon="📊")
p2 = st.Page(nova_transacao, title="Nova Transação", icon="➕")
p3 = st.Page("config.py", title="Configurações", icon="⚙️")
p4 = st.Page(nova_categoria, title="Nova Categoria", icon="➕")
p5 = st.Page(nova_subcategoria, title="Nova Subcategoria", icon="➕")
p6 = st.Page(deletar_transacao, title="Excluir Transação", icon="➖")
p7 = st.Page("tabela.py", title="Transações", icon="📋")


# 3. Agrupando em seções no menu (usando um dicionário)
rotas = {"Menu Principal": [p1], "Administração": []}

if st.user.email == email_adm:
    rotas["Menu Principal"] = [p1, p7, p2, p6]
    rotas["Administração"] = [p3, p4, p5]


# 4. Iniciando a navegação
pg = st.navigation(rotas)
pg.run()
