from langchain.tools import tool, ToolRuntime
from dataclasses import dataclass
from langgraph.types import Command
from langchain.messages import ToolMessage
from utils.metricas import budget_metrics


# 1. Definimos um "Contexto" customizado que o Streamlit passará para a ferramenta.
# Isso pode conter o nome do usuário, permissões, etc.
@dataclass
class ProjetoContext:
    user_name: str
    permissao_admin: bool


@tool
def display_budget_metrics():
    """
    Recupera as métricas de solvência e saúde orçamentária da igreja.
    Esta ferramenta deve ser usada sempre que o usuário perguntar sobre a situação financeira,
    saúde das contas, saldo, margem de segurança ou reserva (cash runway).

    Returns:
        str: Um resumo textual das métricas financeiras para o agente analisar.
    """
    return budget_metrics()


# ==========================================
# FERRAMENTA 2: Ação com ToolRuntime (Bastidores)
# ==========================================
# Usamos ToolRuntime[ProjetoContext] para acessar o contexto que definimos acima [8, 9].
# @tool
# def salvar_relatorio(conteudo: str, runtime: ToolRuntime[ProjetoContext]) -> str | Command:
#     """
#     Usa esta ferramenta para salvar um resumo ou relatório no sistema
#     após a pesquisa, SOMENTE se o usuário solicitar expressamente para salvar.
#     """
#     # O LLM não sabe que "runtime" existe, ele só vai enviar o "conteudo" [8].
#     # O LangChain injeta os dados reais do usuário aqui pra nós [8].
#     nome_usuario = runtime.context.user_name
#     eh_admin = runtime.context.permissao_admin

#     if not eh_admin:
#         # Se não for admin, retornamos um erro disfarçado de ToolMessage para o modelo [10].
#         return ToolMessage(
#             content=f"Erro de permissão: {nome_usuario} não tem autorização para salvar relatórios.",
#             tool_call_id=runtime.tool_call_id
#         )

#     print(f"💾 [Sistema] Salvando o relatório para o usuário {nome_usuario}...")

#     # Se der certo, retornamos o texto de sucesso que o modelo usará na resposta
#     return "Relatório salvo com sucesso no banco de dados!"
