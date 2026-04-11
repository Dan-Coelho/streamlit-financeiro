# PRD — Geração de Relatório em PDF (Formato Slide)

## Visão Geral

**Funcionalidade:** Geração de relatório financeiro em PDF no formato paisagem (slide), acionada pelo agente de IA.

**Objetivo:** Permitir que o agente de IA (`src/agent.py`) invoque ferramentas em `src/tools.py` para gerar um relatório executivo em PDF com tabelas, métricas e gráficos financeiros da IPnovaEusébio, pronto para apresentação em reuniões de liderança.

**Usuários alvo:** Liderança da IPnovaEusébio (pastores, diáconos, tesoureiros) que precisam de relatórios prontos para apresentação.

---

## Problema

Atualmente, o painel Streamlit exibe dados financeiros interativamente, mas não há como exportar um resumo executivo formatado para apresentação física ou digital fora do sistema. A liderança precisa de um documento portátil, imprimível e visualmente consistente para reuniões e assembleias.

---

## Solução Proposta

Criar um conjunto de ferramentas LangChain (`@tool`) em `src/tools.py` que:

1. Buscam dados do Supabase via `utils/database.py` e `utils/metricas.py`
2. Transformam DataFrames em HTML via `pandas.to_html()`
3. Renderizam o HTML final usando templates Jinja2 com CSS estilizado
4. Convertem o HTML para páginas PDF individuais via `pdfkit`
5. Montam as páginas em um único documento PDF via `pypdf`
6. Retornam o caminho do arquivo PDF gerado para que o agente possa disponibilizá-lo no Streamlit

O PDF final deve ter **orientação paisagem (A4 landscape)**, layout de slides com uma seção por página, paleta de cores escura consistente com o tema atual do painel.

---

## Arquitetura

```
src/tools.py
  ├── gerar_relatorio_financeiro()        ← ferramenta principal chamada pelo agente
  │
src/report/
  ├── builder.py                          ← orquestra a criação das seções do PDF
  ├── renderer.py                         ← renderiza HTML via Jinja2 e converte com pdfkit
  ├── assembler.py                        ← monta páginas individuais com pypdf
  └── templates/
        ├── base.html                     ← layout base com variáveis CSS
        ├── slide_capa.html               ← capa do relatório
        ├── slide_metricas.html           ← slide de métricas financeiras
        ├── slide_tabela_receitas.html    ← slide de tabela de receitas
        ├── slide_tabela_despesas.html    ← slide de tabela de despesas
        └── slide_resumo.html             ← slide de resumo e diagnóstico do agente
```

---

## Especificações Técnicas

### Novas Dependências

| Pacote    | Versão mínima | Finalidade                                          |
|-----------|---------------|-----------------------------------------------------|
| `jinja2`  | `>=3.1`       | Renderização de templates HTML com CSS embutido     |
| `pdfkit`  | `>=1.0`       | Conversão de HTML → PDF (wrapper do `wkhtmltopdf`)  |
| `pypdf`   | `>=4.0`       | Leitura, mesclagem e montagem de páginas PDF        |

> **Nota:** `pdfkit` requer a instalação do binário `wkhtmltopdf` no ambiente de execução. Documentar no README.

### Configuração do PDF (pdfkit)

```python
PDFKIT_OPTIONS = {
    "page-size": "A4",
    "orientation": "Landscape",
    "margin-top": "10mm",
    "margin-right": "10mm",
    "margin-bottom": "10mm",
    "margin-left": "10mm",
    "encoding": "UTF-8",
    "enable-local-file-access": True,
}
```

### Ferramenta do Agente — `gerar_relatorio_financeiro`

**Assinatura:**
```python
@tool
def gerar_relatorio_financeiro(
    data_inicio: str,
    data_fim: str,
    diagnostico_agente: str
) -> str:
    """
    Gera um relatório financeiro completo em PDF no formato slide (paisagem).
    ...
    """
```

**Parâmetros:**
- `data_inicio` (str): Data de início do período no formato `YYYY-MM-DD`
- `data_fim` (str): Data de fim do período no formato `YYYY-MM-DD`
- `diagnostico_agente` (str): Texto de diagnóstico/recomendações redigido pelo próprio agente para incluir no slide de resumo

**Retorno:**
- `str`: Caminho absoluto do arquivo PDF gerado (ex: `reports/relatorio_2025_01.pdf`) ou mensagem de erro

---

## Slides do Relatório

### Slide 1 — Capa
- Logo da Igreja (`static/`)
- Título: "Relatório Financeiro — IPnovaEusébio"
- Período coberto (data_inicio → data_fim)
- Data de geração
- Rodapé com aviso de confidencialidade

### Slide 2 — Métricas de Saúde Financeira
Dados de `utils/metricas.calcular_metricas_orcamento()`:
- Saldo Atual Total
- Média Mensal de Receitas
- Média Mensal de Despesas Recorrentes
- Margem de Segurança (%)
- Cash Runway (meses)
- Indicador visual: status **Estável / Alerta / Crítico**

### Slide 3 — Tabela de Receitas
Dados de `utils/database.carregar_transacoes()` filtrados por `tipo == "Receita"` e pelo período:
- Colunas: Data, Descrição, Categoria, Subcategoria, Valor
- Total ao final da tabela
- Gerado via `pandas.to_html()`

### Slide 4 — Tabela de Despesas
Dados de `utils/database.carregar_transacoes()` filtrados por `tipo == "Despesa"` e pelo período:
- Colunas: Data, Descrição, Categoria, Subcategoria, Valor (absoluto)
- Total ao final da tabela
- Gerado via `pandas.to_html()`

### Slide 5 — Resumo e Diagnóstico do Agente
- Texto gerado pelo agente (`diagnostico_agente`) formatado com markdown → HTML
- Seções: Resumo Executivo, Diagnóstico (badge de status), Recomendações

---

## Estilo Visual (CSS)

Utilizar as variáveis de cor do tema escuro já definido em `utils/utils.py` como referência:

```css
:root {
  --color-bg-primary: #0f1117;
  --color-bg-secondary: #1a1d27;
  --color-accent: #4f8ef7;
  --color-text-primary: #ffffff;
  --color-text-secondary: #a0aec0;
  --color-success: #48bb78;
  --color-danger: #fc8181;
}
```

Cada slide deve ter:
- Fundo escuro consistente com o painel
- Cabeçalho fixo com nome da igreja e número do slide
- Rodapé com data de geração
- Fonte: sans-serif (ex: Arial ou Inter via Google Fonts embutida)

---

## Integração com o Agente (`src/agent.py`)

1. Importar a nova ferramenta em `src/agent.py`
2. Adicionar `gerar_relatorio_financeiro` à lista `tools=[...]` do `create_agent`
3. Adicionar instrução no `system_prompt` descrevendo quando usar a ferramenta:

```
Geração de Relatório PDF:
Quando o usuário solicitar um relatório, resumo imprimível ou documento para apresentação,
use a ferramenta `gerar_relatorio_financeiro`. Antes de chamar a ferramenta, redija o
diagnóstico financeiro completo e passe-o como argumento `diagnostico_agente`.
Informe ao usuário que o arquivo foi gerado e onde ele pode ser baixado.
```

4. No `app.py`, após o retorno do agente, verificar se a resposta contém um caminho de arquivo `.pdf` e, em caso positivo, exibir um botão de download via `st.download_button`.

---

## Considerações de Segurança e Qualidade

- Relatórios salvos em diretório temporário (`/tmp` ou `reports/`) com nomes únicos por timestamp
- Não expor caminhos internos ao usuário final; apenas disponibilizar o download
- Validar as datas de entrada antes de consultar o banco
- Tratar exceções em cada etapa (busca de dados, renderização, conversão) com mensagens de erro claras para o agente retransmitir ao usuário
- Apenas usuários autenticados (verificar `st.experimental_user`) podem acionar a geração

---

## Tasks de Implementação

### TASK-01 — Adicionar dependências ao projeto
- Adicionar `jinja2`, `pdfkit` e `pypdf` ao `pyproject.toml`
- Rodar `uv sync` para instalar
- Documentar no `README.md` a instalação do `wkhtmltopdf` no ambiente

### TASK-02 — Criar estrutura de diretórios
- Criar `src/report/` com `__init__.py`
- Criar `src/report/builder.py`, `src/report/renderer.py`, `src/report/assembler.py`
- Criar `src/report/templates/` com os 5 arquivos HTML de slides

### TASK-03 — Criar templates Jinja2 com CSS
- `base.html`: layout base com `<head>` incluindo CSS completo do tema escuro, slots `{% block content %}` e `{% block title %}`
- `slide_capa.html`: extends base, exibe logo, título, período e data de geração
- `slide_metricas.html`: extends base, recebe dict de métricas e renderiza cards com badge de status
- `slide_tabela_receitas.html`: extends base, recebe HTML da tabela e total
- `slide_tabela_despesas.html`: extends base, recebe HTML da tabela e total
- `slide_resumo.html`: extends base, recebe texto do diagnóstico do agente

### TASK-04 — Implementar `src/report/renderer.py`
- Função `renderizar_slide(template_name: str, contexto: dict) -> str`: renderiza template Jinja2 → string HTML
- Função `html_para_pdf(html: str, caminho_saida: str) -> str`: converte HTML → PDF via `pdfkit` com as opções de paisagem A4

### TASK-05 — Implementar `src/report/assembler.py`
- Função `montar_relatorio(caminhos_pdf: list[str], caminho_final: str) -> str`: usa `pypdf.PdfWriter` para mesclar páginas individuais em um único PDF
- Limpar arquivos intermediários após a montagem

### TASK-06 — Implementar `src/report/builder.py`
- Função `construir_relatorio(data_inicio, data_fim, diagnostico_agente) -> str`:
  1. Chama `carregar_transacoes()` e filtra pelo período
  2. Chama `calcular_metricas_orcamento()` para métricas
  3. Gera `pandas.to_html()` para receitas e despesas
  4. Renderiza cada slide via `renderer.renderizar_slide()`
  5. Converte cada slide para PDF via `renderer.html_para_pdf()`
  6. Monta o PDF final via `assembler.montar_relatorio()`
  7. Retorna o caminho do arquivo final

### TASK-07 — Implementar a ferramenta em `src/tools.py`
- Adicionar `@tool gerar_relatorio_financeiro(data_inicio, data_fim, diagnostico_agente)` que chama `builder.construir_relatorio()`
- Tratar exceções e retornar mensagem de erro amigável se falhar

### TASK-08 — Integrar ferramenta ao agente em `src/agent.py`
- Importar `gerar_relatorio_financeiro` de `src/tools`
- Adicionar à lista `tools=[...]`
- Adicionar instrução de uso da ferramenta no `system_prompt`

### TASK-09 — Integrar download no `app.py`
- Após receber resposta do agente, detectar se foi gerado um arquivo PDF
- Exibir `st.download_button` com o conteúdo binário do arquivo
- Limpar o arquivo temporário após o download

### TASK-10 — Testes e validação
- Testar geração com período com dados e com período sem dados
- Validar layout visual em PDF aberto no visualizador de slides
- Verificar que o agente aciona a ferramenta corretamente ao ser solicitado
- Rodar `pytest` e `ruff check .` e garantir zero erros

---

## Critérios de Aceitação

- [ ] O agente gera o PDF ao receber uma solicitação natural como "gere um relatório do mês de março"
- [ ] O PDF tem exatamente 5 slides em orientação paisagem A4
- [ ] Cada slide exibe corretamente os dados do período solicitado
- [ ] O slide de métricas mostra o badge de status correto (Estável / Alerta / Crítico)
- [ ] O slide de resumo contém o diagnóstico redigido pelo agente
- [ ] Um botão de download aparece no Streamlit após a geração
- [ ] O sistema lida com períodos sem dados sem crashar
- [ ] Nenhum secret ou credencial é exposto no PDF gerado
