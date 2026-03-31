import pandas as pd
import streamlit as st
from st_supabase_connection import SupabaseConnection
from utils.logger import logger


# Conexão com Supabase usando o conector oficial do Streamlit
try:
    # O conector procura por [connections.supabase] no secrets.toml
    conn = st.connection("supabase", type=SupabaseConnection)
    logger.info("Conexão com Supabase estabelecida com sucesso!")
except Exception as e:
    st.error(
        "Erro ao conectar ao Supabase. Verifique se as chaves SUPABASE_URL e SUPABASE_KEY estão configuradas em .streamlit/secrets.toml"
    )
    logger.error(f"Erro ao conectar ao Supabase: {e}")
    st.stop()


def adicionar_categoria(nome):
    """Adiciona uma nova categoria ao banco de dados Supabase."""
    try:
        conn.table("categorias").insert({"nome": nome}).execute()
        logger.info(f"Categoria '{nome}' adicionada com sucesso!")
        return True
    except Exception as e:
        st.error(f"Erro ao adicionar categoria: {e}")
        logger.error(f"Erro ao adicionar categoria: {e}")
        return False


def adicionar_subcategoria(nome, categoria_id):
    """Adiciona uma nova subcategoria vinculada a uma categoria no Supabase."""
    try:
        conn.table("subcategorias").insert(
            {"nome": nome, "categoria_id": categoria_id}
        ).execute()
        logger.info(f"Subcategoria '{nome}' adicionada com sucesso!")
        return True
    except Exception as e:
        st.error(f"Erro ao adicionar subcategoria: {e}")
        logger.error(f"Erro ao adicionar subcategoria: {e}")
        return False


def buscar_categorias():
    """Retorna a lista de categorias cadastradas."""
    try:
        response = conn.table("categorias").select("id, nome").execute()
        return response.data
    except Exception as e:
        st.error(f"Erro ao buscar categorias: {e}")
        logger.error(f"Erro ao buscar categorias: {e}")
        return []


def buscar_subcategorias(categoria_id=None):
    """Retorna a lista de subcategorias, opcionalmente filtrada por categoria_id."""
    try:
        client = conn.client  # acessa o cliente supabase-py diretamente
        query = client.table("subcategorias").select("id, nome, categoria_id")
        # query = conn.table("subcategorias").select("id, nome, categoria_id")
        if categoria_id:
            query = query.eq("categoria_id", categoria_id)

        response = query.order("nome").execute()
        return response.data
    except Exception as e:
        st.error(f"Erro ao buscar subcategorias: {e}")
        logger.error(f"Erro ao buscar subcategorias: {e}")
        return []


def adicionar_transacao(
    data, descricao, valor, recorrente, categoria_id, subcategoria_id
):
    """Adiciona uma nova transação ao banco de dados Supabase."""
    tipo = "Receita" if valor > 0 else "Despesa"
    try:
        conn.table("transacoes").insert(
            {
                "data": str(data),
                "descricao": descricao,
                "valor": valor,
                "recorrente": bool(recorrente),
                "categoria_id": categoria_id,
                "subcategoria_id": subcategoria_id,
                "tipo": tipo,
            }
        ).execute()
        logger.info("Transação adicionada com sucesso!")
        st.toast("Transação salva com sucesso!")
        return True
    except Exception as e:
        st.error(f"Erro ao adicionar transação: {e}")
        logger.error(f"Erro ao adicionar transação: {e}")
        return False


def carregar_transacoes():
    """Carrega todas as transações com os nomes das categorias e subcategorias."""
    try:
        # No Supabase, fazemos o join via select() especificando as relações
        query = (
            "id, data, descricao, valor, recorrente, tipo, "
            "categorias(nome), subcategorias(nome)"
        )
        response = (
            conn.table("transacoes").select(query).order("data", desc=True).execute()
        )

        if not response.data:
            logger.info("Nenhuma transação encontrada.")
            return pd.DataFrame()

        # Transformar os dados aninhados do Supabase em colunas planas para o DataFrame
        df_list = []
        for item in response.data:
            flat_item = {
                "id": item["id"],
                "data": item["data"],
                "descricao": item["descricao"],
                "valor": item["valor"],
                "recorrente": item["recorrente"],
                "tipo": item["tipo"],
                "categoria": item["categorias"]["nome"]
                if item.get("categorias")
                else None,
                "subcategoria": item["subcategorias"]["nome"]
                if item.get("subcategorias")
                else None,
            }
            df_list.append(flat_item)

        transacoes = pd.DataFrame(df_list)
        transacoes["data"] = pd.to_datetime(transacoes["data"])
        transacoes["recorrente"] = transacoes["recorrente"].astype(bool)
        transacoes.set_index("data", inplace=True)

        return transacoes
    except Exception as e:
        st.error(f"Erro ao carregar transações: {e}")
        logger.error(f"Erro ao carregar transações: {e}")
        return pd.DataFrame()


def excluir_transacao(id_transacao):
    """Exclui uma transação pelo ID no Supabase."""
    try:
        conn.table("transacoes").delete().eq("id", id_transacao).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao excluir transação: {e}")
        logger.error(f"Erro ao excluir transação: {e}")
        return False


def atualizar_transacao(
    id_transacao, data, descricao, valor, recorrente, categoria_id, subcategoria_id
):
    """Atualiza uma transação existente no Supabase."""
    tipo = "Receita" if valor > 0 else "Despesa"
    try:
        conn.table("transacoes").update(
            {
                "data": str(data),
                "descricao": descricao,
                "valor": valor,
                "recorrente": bool(recorrente),
                "categoria_id": categoria_id,
                "subcategoria_id": subcategoria_id,
                "tipo": tipo,
            }
        ).eq("id", id_transacao).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar transação: {e}")
        logger.error(f"Erro ao atualizar transação: {e}")
        return False
