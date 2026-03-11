import pandas as pd
import streamlit as st
from sqlalchemy import text


conn = st.connection("financeiro", type="sql")

with conn.session as s:
    s.execute(
        text(
            "CREATE TABLE IF NOT EXISTS categorias(id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL UNIQUE);"
        )
    )
    s.execute(
        text(
            "CREATE TABLE IF NOT EXISTS subcategorias(id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, categoria_id INTEGER NOT NULL, FOREIGN KEY (categoria_id) REFERENCES categorias (id) ON DELETE CASCADE, UNIQUE(nome, categoria_id));"
        )
    )
    s.execute(
        text("""
        CREATE TABLE IF NOT EXISTS transacoes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data DATE NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            recorrente BOOLEAN DEFAULT 0,
            categoria_id INTEGER,
            subcategoria_id INTEGER,
            tipo TEXT NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (categoria_id) REFERENCES categorias (id),
            FOREIGN KEY (subcategoria_id) REFERENCES subcategorias (id)
        );
    """)
    )
    s.commit()


def adicionar_categoria(nome):
    """Adiciona uma nova categoria ao banco de dados."""
    with conn.session as s:
        try:
            comando = text("INSERT INTO categorias (nome) VALUES (:nome)")
            s.execute(comando, params=dict(nome=nome))
            s.commit()
            return True
        except Exception:
            return False


def adicionar_subcategoria(nome, categoria_id):
    """Adiciona uma nova subcategoria vinculada a uma categoria."""
    with conn.session as s:
        try:
            comando = text(
                "INSERT INTO subcategorias (nome, categoria_id) VALUES (:nome, :categoria_id)"
            )
            s.execute(comando, params=dict(nome=nome, categoria_id=categoria_id))
            s.commit()
            return True
        except Exception:
            return False


def buscar_categorias():
    """Retorna a lista de categorias cadastradas."""
    categorias = conn.query("SELECT id, nome FROM categorias", ttl=60)
    return categorias.to_dict(orient="records")


def buscar_subcategorias(categoria_id=None):
    """Retorna a lista de subcategorias, opcionalmente filtrada por categoria_id."""
    if categoria_id:
        subcategorias = conn.query(
            "SELECT id, nome FROM subcategorias WHERE categoria_id = :categoria_id ORDER BY nome",
            params=dict(categoria_id=categoria_id),
            ttl=60,
        )
    else:
        subcategorias = conn.query(
            "SELECT id, nome FROM subcategorias ORDER BY nome", ttl=60
        )

    return subcategorias.to_dict(orient="records")


def adicionar_transacao(
    data, descricao, valor, recorrente, categoria_id, subcategoria_id
):
    """Adiciona uma nova transação ao banco de dados."""
    tipo = "Receita" if valor > 0 else "Despesa"
    with conn.session as s:
        comando = text("""
            INSERT INTO transacoes (data, descricao, valor, recorrente, categoria_id, subcategoria_id, tipo)
            VALUES (:data, :descricao, :valor, :recorrente, :categoria_id, :subcategoria_id, :tipo)
        """)
        s.execute(
            comando,
            params=dict(
                data=data,
                descricao=descricao,
                valor=valor,
                recorrente=1 if recorrente else 0,
                categoria_id=categoria_id,
                subcategoria_id=subcategoria_id,
                tipo=tipo,
            ),
        )
        s.commit()


def carregar_transacoes():
    """Carrega todas as transações com os nomes das categorias e subcategorias."""
    query = """
        SELECT 
            t.id, t.data, t.descricao, t.valor, t.recorrente, t.tipo,
            c.nome as categoria, 
            s.nome as subcategoria
        FROM transacoes t
        LEFT JOIN categorias c ON t.categoria_id = c.id
        LEFT JOIN subcategorias s ON t.subcategoria_id = s.id
        ORDER BY t.data DESC
    """
    transacoes = conn.query(query, ttl=60)

    if not transacoes.empty:
        transacoes["data"] = pd.to_datetime(transacoes["data"])
        transacoes["recorrente"] = transacoes["recorrente"].astype(bool)
        transacoes.set_index("data", inplace=True)

    return transacoes


def excluir_transacao(id_transacao):
    """Exclui uma transação pelo ID."""
    with conn.session as s:
        comando = text("DELETE FROM transacoes WHERE id = :id_transacao")
        s.execute(comando, params=dict(id_transacao=id_transacao))
        s.commit()


def atualizar_transacao(
    id_transacao, data, descricao, valor, recorrente, categoria_id, subcategoria_id
):
    """Atualiza uma transação existente."""
    tipo = "Receita" if valor > 0 else "Despesa"
    with conn.session as s:
        comando = text("""
            UPDATE transacoes 
            SET data = :data, descricao = :descricao, valor = :valor, recorrente = :recorrente,
                categoria_id = :categoria_id, subcategoria_id = :subcategoria_id, tipo = :tipo
            WHERE id = :id_transacao
        """)
        s.execute(
            comando,
            params=dict(
                data=data,
                descricao=descricao,
                valor=valor,
                recorrente=1 if recorrente else 0,
                categoria_id=categoria_id,
                subcategoria_id=subcategoria_id,
                tipo=tipo,
                id_transacao=id_transacao,
            ),
        )
        s.commit()
