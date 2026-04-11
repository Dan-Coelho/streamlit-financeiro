import base64
import pandas as pd
import locale
import tempfile
import sys
import pdfkit
from typing import Optional
import html as _html_module
import os
import re
from datetime import datetime
from datetime import date
from pathlib import Path
import plotly.io as pio
#from utils.db import carregar_transacoes
from utils.database import carregar_transacoes
from jinja2 import Environment, FileSystemLoader, select_autoescape
from utils.logger import logger
import plotly.express as px
from pypdf import PdfWriter


df = carregar_transacoes()

_jinja_env = Environment(
    loader=FileSystemLoader('src/report/templates'),
    autoescape=select_autoescape(["html"]),
)

# Opções do pdfkit para PDF A4 paisagem
# Flags booleanas (sem valor) devem ser None — pdfkit as converte para --flag
_PDFKIT_OPTIONS: dict[str, str | None] = {
    "page-size": "A4",
    "orientation": "Landscape",
    "margin-top": "0mm",
    "margin-right": "0mm",
    "margin-bottom": "0mm",
    "margin-left": "0mm",
    "encoding": "UTF-8",
    "enable-local-file-access": None,
    "print-media-type": None,
    "disable-smart-shrinking": None,
    "quiet": None,
}

# Caminhos comuns de instalação do wkhtmltopdf no Windows
_WKHTMLTOPDF_WINDOWS_PATHS = [
    r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
    r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe",
]


def _get_pdfkit_config() -> Optional[object]:
    """
    Retorna a configuração com o caminho do executável wkhtmltopdf.
    No Windows, tenta localizar automaticamente nos caminhos padrão de instalação.
    Retorna None se estiver no PATH (Linux/macOS ou PATH configurado).
    """
    if sys.platform == "win32":
        for caminho in _WKHTMLTOPDF_WINDOWS_PATHS:
            if Path(caminho).exists():
                logger.debug(f"wkhtmltopdf encontrado em: {caminho}")
                return pdfkit.configuration(wkhtmltopdf=caminho)
        logger.warning(
            "wkhtmltopdf não encontrado nos caminhos padrão do Windows. "
            "Certifique-se de que está instalado e no PATH, ou instale em: "
            "C:\\Program Files\\wkhtmltopdf\\bin\\"
        )
    return None


def mont_relatorio(caminhos_pdf: list[str], caminho_final: str) -> str:
    """
    Mescla múltiplos arquivos PDF em um único documento e remove os temporários.

    Args:
        caminhos_pdf: Lista ordenada de caminhos para os PDFs de cada slide.
        caminho_final: Caminho onde o PDF consolidado será salvo.

    Returns:
        caminho_final confirmado após a montagem bem-sucedida.

    Raises:
        FileNotFoundError: Se algum PDF intermediário não for encontrado.
        ValueError: Se a lista de PDFs estiver vazia.
    """
    if not caminhos_pdf:
        raise ValueError("A lista de PDFs para montar está vazia.")

    ausentes = [p for p in caminhos_pdf if not Path(p).exists()]
    if ausentes:
        raise FileNotFoundError(
            f"PDFs intermediários não encontrados: {ausentes}"
        )

    writer = PdfWriter()

    for caminho in caminhos_pdf:
        writer.append(caminho)
        logger.debug(f"Slide adicionado ao relatório: {caminho}")

    Path(caminho_final).parent.mkdir(parents=True, exist_ok=True)

    with open(caminho_final, "wb") as f:
        writer.write(f)

    logger.info(f"Relatório PDF montado com {len(caminhos_pdf)} slides: {caminho_final}")

    # Remove arquivos temporários após montagem bem-sucedida
    for caminho in caminhos_pdf:
        try:
            os.remove(caminho)
            logger.debug(f"Temporário removido: {caminho}")
        except OSError as e:
            logger.warning(f"Não foi possível remover temporário '{caminho}': {e}")

    return caminho_final

def render_slide(template_name: str, contexto: dict) -> str:
    """
    Renderiza um template Jinja2 com o contexto fornecido.

    Args:
        template_name: Nome do arquivo de template (ex: 'slide_capa.html').
        contexto: Dicionário de variáveis passadas ao template.

    Returns:
        String HTML renderizada.

    Raises:
        jinja2.TemplateNotFound: Se o template não existir.
    """
    template = _jinja_env.get_template(template_name)
    html = template.render(**contexto)
    logger.debug(f"Template '{template_name}' renderizado ({len(html)} caracteres)")
    return html


def html_to_pdf(html: str, caminho_saida: str) -> str:
    """
    Converte uma string HTML em um arquivo PDF (paisagem A4) via pdfkit.

    Args:
        html: Conteúdo HTML a converter.
        caminho_saida: Caminho completo onde o PDF será salvo.

    Returns:
        caminho_saida confirmado após geração bem-sucedida.

    Raises:
        OSError: Se o wkhtmltopdf não estiver instalado ou inacessível.
        IOError: Se a conversão falhar.
    """
    # Garante que o diretório de destino existe
    Path(caminho_saida).parent.mkdir(parents=True, exist_ok=True)

    try:
        config = _get_pdfkit_config()
        pdfkit.from_string(
            html,
            caminho_saida,
            options=_PDFKIT_OPTIONS,
            configuration=config,
        )
    except OSError as e:
        msg = str(e)
        logger.error(f"Falha ao converter HTML para PDF: {msg}")
        if "wkhtmltopdf" in msg.lower() and ("not found" in msg.lower() or "no such" in msg.lower()):
            raise OSError(
                "wkhtmltopdf não encontrado. Instale-o conforme as instruções do README."
            ) from e
        raise OSError(f"Falha na conversão HTML→PDF (wkhtmltopdf): {msg}") from e

    logger.debug(f"PDF gerado: {caminho_saida}")
    return caminho_saida


def texto_para_html(texto: str) -> str:
    """
    Converte texto com Markdown básico em HTML seguro para o slide de resumo.
    Suporta: # / ## / ### headings, **bold**, listas (- / *) e parágrafos.
    """
    linhas = texto.split("\n")
    resultado: list[str] = []
    em_lista = False

    def _negrito(s: str) -> str:
        return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)

    def _fechar_lista():
        if em_lista:
            resultado.append("</ul>")

    for linha in linhas:
        linha_esc = _html_module.escape(linha.rstrip())
        strip = linha_esc.strip()

        # Headings: detecta pela quantidade de # no início
        if strip.startswith("### "):
            if em_lista:
                resultado.append("</ul>")
                em_lista = False
            resultado.append(f"<h4>{_negrito(strip[4:])}</h4>")

        elif strip.startswith("## "):
            if em_lista:
                resultado.append("</ul>")
                em_lista = False
            resultado.append(f"<h3>{_negrito(strip[3:])}</h3>")

        elif strip.startswith("# "):
            if em_lista:
                resultado.append("</ul>")
                em_lista = False
            resultado.append(f"<h2>{_negrito(strip[2:])}</h2>")

        elif strip.startswith("- ") or strip.startswith("* "):
            if not em_lista:
                resultado.append("<ul>")
                em_lista = True
            resultado.append(f"<li>{_negrito(strip[2:])}</li>")

        elif not strip:
            if em_lista:
                resultado.append("</ul>")
                em_lista = False

        else:
            if em_lista:
                resultado.append("</ul>")
                em_lista = False
            resultado.append(f"<p>{_negrito(strip)}</p>")

    if em_lista:
        resultado.append("</ul>")

    return "\n".join(resultado)

def _fmt_data(data_str: str) -> str:
    """Converte YYYY-MM-DD para DD/MM/YYYY."""
    return datetime.strptime(data_str, "%Y-%m-%d").strftime("%d/%m/%Y")

def _fmt_brl(valor: float) -> str:
    """Formata um número como moeda brasileira (sem o prefixo R$)."""
    #return f"{abs(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    # com locale
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    return locale.currency(abs(valor), grouping=True)


def _fig_to_b64(fig) -> str:
    """Converte figura Plotly para PNG codificado em base64 (requer kaleido)."""
    img_bytes = pio.to_image(fig, format="png", width=700, height=420, scale=1.5)
    return base64.b64encode(img_bytes).decode("utf-8")




def gerar_dados_gerais(dataframe):
  
  receitas = df[df["tipo"] == "Receita"]
  despesas = df[df["tipo"] == "Despesa"]
  data_inicio = date(2025, 1, 1)
  data_inicio = pd.to_datetime(data_inicio)
  data_fim = date(2026, 3, 31)
  data_fim = pd.to_datetime(data_fim)
  periodo = data_fim - data_inicio
  logger.info(f"Gerando dados para relatório: {data_inicio} → {data_fim}")
  receitas = receitas.iloc[:-1]
  receitas = receitas[(receitas.index >= data_inicio) & (receitas.index <= data_fim)]
  despesas = despesas[(despesas.index >= data_inicio) & (despesas.index <= data_fim)]
  copia_despesas = despesas.copy()
  copia_receitas = receitas.copy()
  receitas_agrupadas = copia_receitas.groupby("categoria")["valor"].sum().reset_index()
  despesas_agrupadas = (
        copia_despesas.groupby("categoria")["valor"].sum().abs().reset_index()
    )
  dict_dados = {}

  if df.empty:
      logger.info("Nenhuma transação registrada ainda. Use a barra lateral para começar!")
  else:
      # Métricas Rápidas
      receitas_total = receitas["valor"].sum()
      despesas_total = abs(despesas["valor"].sum())
      saldo = receitas_total - despesas_total
      # Cálculo da média de despesas
      despesas_mensais = copia_despesas.resample("ME")["valor"].sum()
      media_mensal_despesas = abs(despesas_mensais.iloc[:-1]).mean()
      # Cálculo da média de receitas
      receitas_mensais = copia_receitas.resample("ME")["valor"].sum()
      media_mensal_receitas = receitas_mensais.iloc[:-1].mean()
      # Gráficos de Despesa
      fi_despesas = px.pie(
                despesas_agrupadas,
                names="categoria",
                values="valor",
                color_discrete_sequence=px.colors.qualitative.Plotly,
                hover_data=["valor"],
            )
      fi_despesas.update_layout(
                paper_bgcolor="white",
                plot_bgcolor="white",
                font=dict(color="#2d3436"),
            )
      # Gráficos de Receita
      fi_receitas = px.pie(
                receitas_agrupadas,
                names="categoria",
                values="valor",
                color_discrete_sequence=px.colors.qualitative.Plotly,
            )
      fi_receitas.update_layout(
                paper_bgcolor="white",
                plot_bgcolor="white",
                font=dict(color="#2d3436"),
            )

  dict_dados['total_receitas'] = _fmt_brl(receitas_total)
  dict_dados['total_despesas'] = _fmt_brl(despesas_total)
  dict_dados['saldo_atual'] = _fmt_brl(saldo)
  dict_dados['media_mensal_despesas'] = _fmt_brl(media_mensal_despesas)
  dict_dados['media_mensal_receitas'] = _fmt_brl(media_mensal_receitas)
  dict_dados['fi_despesas'] = _fig_to_b64(fi_despesas)
  dict_dados['fi_receitas'] = _fig_to_b64(fi_receitas)

  return dict_dados




_REPORTS_DIR = 'reports'
dados = gerar_dados_gerais(dataframe=df)
# Converte logo para base64 para funcionar no wkhtmltopdf
_LOGO_PATH = Path('static/logoescuro.jpg')
_logo_b64 = base64.b64encode(_LOGO_PATH.read_bytes()).decode('utf-8') if _LOGO_PATH.exists() else ''
# Contexto compartilhado entre todos os slides
data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M")
ctx_base = {
    "data_geracao": data_geracao,
}
diagnostico = '''
# CONTEXTO:
## Considerando o fato que a IPNova Eusébio está em um período de transição se tornar uma congregação, devemos acompanhar de perto sua situação financeira.
# PONTO DE ATENÇÃO:
## Estamos prestes a assumir as custas com o salário do Pastor. Para essas custas, foi elaborado um cronograma que prevê um aumento percentual crescente de 12,5 por cento a cada dois meses. Em abril desse ano a responsabilidade da IPNova Eusébio com o seu Pastor está em 37,5 por cento de seu salário.
'''
slides = [
    ("slide_capa.html", {
        **ctx_base, "slide_num": 1,
        "logo_b64": _logo_b64,
    }),
    ("slide_metricas_receitas.html", {
        **ctx_base, "slide_num": 2,
        "media_mensal_receitas": dados['media_mensal_receitas'],
        "fi_receitas": dados['fi_receitas'],
    }),
    ("slide_metricas_despesas.html", {
        **ctx_base, "slide_num": 3,
        "media_mensal_despesas": dados['media_mensal_despesas'],
        "fi_despesas": dados['fi_despesas'],
    }),
    ("slide_resultado.html", {
        **ctx_base, "slide_num": 4,
        "total_receitas": dados['total_receitas'],
        "total_despesas": dados['total_despesas'],
        "saldo_atual": dados['saldo_atual'],
        "media_mensal_receitas": dados['media_mensal_receitas'],
        "media_mensal_despesas": dados['media_mensal_despesas'],
    }),
    ("slide_resumo.html", {
        **ctx_base, "slide_num": 5,
        "diagnostico_html": texto_para_html(diagnostico),
    }),
]
# Renderiza cada slide → HTML → PDF temporário
tmp_dir = tempfile.mkdtemp(prefix="ipnj_report_")
pdfs_tmp: list[str] = []

for i, (template, ctx) in enumerate(slides, start=1):
    html = render_slide(template, ctx)
    caminho_tmp = os.path.join(tmp_dir, f"slide_{i:02d}.pdf")
    html_to_pdf(html, caminho_tmp)
    pdfs_tmp.append(caminho_tmp)
    logger.debug(f"Slide {i}/5 gerado: {caminho_tmp}")

# Monta o PDF final
timestamp    = datetime.now().strftime("%Y%m%d_%H%M%S")
caminho_final = str(Path(_REPORTS_DIR) / f"relatorio_{timestamp}.pdf")

mont_relatorio(pdfs_tmp, caminho_final)