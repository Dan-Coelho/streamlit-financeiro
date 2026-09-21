# Dashboard Financeiro IPNova Eusébio

Aplicação web em Streamlit para registrar, consultar e analisar as finanças da IPNova Eusébio. Os dados são persistidos no Supabase e apresentados em páginas para dashboard, orçamento, histórico de transações e administração de categorias.

O projeto também contém uma integração experimental com LangChain/LangGraph para responder perguntas sobre a saúde orçamentária usando as métricas calculadas pela aplicação, além de um módulo separado para geração de relatórios em PDF.

## Índice

- [Funcionalidades](#funcionalidades)
- [Stack](#stack)
- [Pré-requisitos](#pré-requisitos)
- [Configuração local](#configuração-local)
- [Execução](#execução)
- [Arquitetura](#arquitetura)
- [Fluxos principais](#fluxos-principais)
- [Modelo de dados esperado](#modelo-de-dados-esperado)
- [Configuração do Supabase](#configuração-do-supabase)
- [Agente de orçamento](#agente-de-orçamento)
- [Relatórios PDF](#relatórios-pdf)
- [Testes e qualidade](#testes-e-qualidade)
- [Manutenção](#manutenção)
- [Limitações conhecidas](#limitações-conhecidas)

## Funcionalidades

- Login por Google via autenticação nativa do Streamlit.
- Controle de acesso por lista de e-mails autorizados.
- Perfil administrador separado por `email_adm`.
- Cadastro de categorias e subcategorias.
- Cadastro de receitas e despesas, com suporte a transações recorrentes.
- Exclusão e edição de transações.
- Filtros por período, categoria e subcategoria.
- Métricas de receitas, despesas, saldo, médias mensais, margem de segurança e cash runway.
- Gráficos Plotly de saldo acumulado e distribuição por categoria.
- Assistente de orçamento com LangChain, usando memória em processo.
- Templates Jinja2 e conversão para PDF via `wkhtmltopdf` no módulo de relatório.

## Stack

| Área | Tecnologia |
| --- | --- |
| Linguagem | Python 3.13 ou superior |
| Interface | Streamlit 1.54 ou superior |
| Dados | Supabase/PostgreSQL via `st-supabase-connection` |
| Tratamento de dados | pandas |
| Visualização | Plotly e Kaleido |
| IA | LangChain, LangGraph e OpenAI (`gpt-4o-mini`) |
| Relatórios | Jinja2, pdfkit, wkhtmltopdf e pypdf |
| Gerenciamento | `uv` e `uv.lock` |
| Qualidade | pytest e Ruff |

## Pré-requisitos

- Python 3.13.
- `uv` instalado e disponível no PATH.
- Um projeto Supabase com as tabelas descritas em [Modelo de dados esperado](#modelo-de-dados-esperado).
- Credenciais do Supabase.
- Credenciais OAuth do Google configuradas para o login do Streamlit.
- Chave da API da OpenAI para o agente da página de orçamento.
- `wkhtmltopdf` instalado apenas se o módulo de relatório PDF for utilizado.

No Windows, o código procura automaticamente o executável nestes caminhos:

```text
C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe
C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe
```

Também é possível instalar o executável em outro local e adicioná-lo ao PATH.

## Configuração local

### 1. Instalar dependências

Na raiz do projeto:

```bash
uv sync
```

Para ativar o ambiente virtual manualmente no Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Criar os secrets do Streamlit

Crie `.streamlit/secrets.toml`. Esse arquivo é ignorado pelo Git e não deve ser commitado.

Exemplo mínimo, ajustando os valores ao ambiente real:

```toml
emails_autorizados = ["tesouraria@example.org", "lideranca@example.org"]
email_adm = "admin@example.org"

[connections.supabase]
SUPABASE_URL = "https://seu-projeto.supabase.co"
SUPABASE_KEY = "sua-chave-do-supabase"

[openai]
OPENAI_API_KEY = "sua-chave-da-openai"
```

O aplicativo lê diretamente:

- `emails_autorizados`: lista de e-mails que podem acessar o sistema.
- `email_adm`: e-mail que recebe as páginas administrativas.
- `connections.supabase`: configuração usada por `st.connection("supabase", type=SupabaseConnection)`.
- `openai.OPENAI_API_KEY`: chave usada na inicialização do agente de orçamento.

Não coloque credenciais em arquivos Python, no README, em templates ou no histórico do Git.

### 3. Configurar autenticação

O `app.py` usa `st.user.is_logged_in`, `st.login` e `st.logout`. Configure o provedor OAuth conforme a documentação da versão do Streamlit instalada e os valores do seu provedor Google. Depois, valide o fluxo com um e-mail autorizado e um e-mail não autorizado.

## Execução

Inicie o aplicativo principal com:

```bash
uv run streamlit run app.py
```

Ou, com o ambiente virtual ativado:

```bash
streamlit run app.py
```

O Streamlit exibirá a URL local, normalmente `http://localhost:8501`.

### Páginas disponíveis

| Página | Arquivo/entrypoint | Acesso |
| --- | --- | --- |
| Painel Principal | `dashboard.py` | Usuário autorizado |
| Transações | `tabela.py` | Administrador |
| Orçamento | `orcamento.py` | Administrador |
| Nova Transação | `utils.utils.nova_transacao` | Administrador |
| Excluir Transação | `utils.utils.deletar_transacao` | Administrador |
| Nova Categoria | `utils.utils.nova_categoria` | Administrador |
| Nova Subcategoria | `utils.utils.nova_subcategoria` | Administrador |
| Sobre a igreja | `config.py` | Usuário autorizado |

O acesso às páginas é montado em `app.py` com `st.Page` e `st.navigation`. Usuários autorizados que não são administradores recebem apenas o painel e a página institucional.

## Arquitetura

```text
.
├── app.py                  # Entrada principal, autenticação e navegação
├── dashboard.py            # Indicadores e gráficos do painel
├── orcamento.py            # Métricas orçamentárias e chat com o agente
├── tabela.py               # Visualização do histórico de transações
├── config.py               # Página institucional da IPNova Eusébio
├── relatorio.py            # Geração de PDF executada como script/import
├── test_app.py             # Teste legado de exemplo do Streamlit
├── pyproject.toml          # Metadados e dependências
├── uv.lock                 # Lockfile do ambiente uv
├── src/
│   ├── agent.py            # Modelo, prompt, memória e agente LangChain
│   ├── tools.py            # Ferramentas expostas ao agente
│   └── report/
│       ├── __init__.py     # Exporta o builder planejado
│       └── templates/      # Templates Jinja2 dos slides
├── utils/
│   ├── database.py         # Operações de leitura/escrita no Supabase
│   ├── metricas.py         # Cálculos e renderização de métricas/gráficos
│   ├── utils.py            # Componentes de interface e ações do usuário
│   └── logger.py           # Logger colorido para o terminal
├── static/                 # Logos, fotos e demais imagens
└── .streamlit/config.toml  # Configurações de execução do Streamlit
```

### Responsabilidades por módulo

#### `app.py`

É o ponto de entrada. Inicializa valores do `st.session_state`, carrega as regras de autorização, configura a barra lateral e registra as rotas. Não deve conter consultas SQL ou cálculos financeiros; essas responsabilidades ficam em `utils/database.py` e `utils/metricas.py`.

#### `utils/database.py`

Centraliza o acesso ao Supabase. `carregar_transacoes()` retorna um `DataFrame` com a data como índice e com os nomes de categoria/subcategoria achatados nas colunas. A função é cacheada por 60 segundos; após inserir, atualizar ou excluir dados, considere limpar o cache com `carregar_transacoes.clear()` se a interface precisar refletir a alteração imediatamente.

#### `utils/metricas.py`

Implementa os cálculos exibidos no painel. As funções também escrevem diretamente componentes Streamlit. `calcular_metricas_orcamento()` é a exceção principal: calcula e retorna um dicionário sem renderizar a interface, sendo reutilizada pelo agente.

#### `utils/utils.py`

Contém as telas de cadastro/edição/exclusão, os filtros e o CSS global. Essas funções são passadas diretamente para `st.Page`, por isso mudanças em suas assinaturas ou no uso de `st.session_state` podem quebrar a navegação.

#### `src/agent.py` e `src/tools.py`

`src/agent.py` cria o modelo OpenAI, a memória `InMemorySaver` e o agente. `src/tools.py` expõe `display_budget_metrics`, que recarrega os dados e chama `budget_metrics()`. A memória é volátil: reiniciar o processo perde o histórico das conversas.

#### `relatorio.py` e `src/report/templates/`

`relatorio.py` contém funções auxiliares para renderizar templates, converter HTML em PDFs e unir PDFs intermediários. Os templates ficam em `src/report/templates/`. O arquivo também possui código executável no nível do módulo, portanto importá-lo pode consultar o banco e gerar um relatório imediatamente.

## Fluxos principais

### Cadastro de transação

1. O administrador abre `Nova Transação`.
2. `nova_transacao()` consulta categorias e subcategorias no Supabase.
3. Receitas são armazenadas com valor positivo; despesas, com valor negativo.
4. `salvar_e_limpar()` chama `adicionar_transacao()`.
5. `adicionar_transacao()` deriva `tipo` pelo sinal do valor e grava o registro.
6. O cache de transações pode manter dados antigos por até 60 segundos.

### Dashboard

1. `dashboard.py` chama `carregar_transacoes()`.
2. `show_filtros()` atualiza o período e as categorias no `st.session_state`.
3. As funções de métricas filtram o DataFrame pelo índice de datas.
4. Plotly renderiza o saldo acumulado e os gráficos por categoria.

### Consulta com IA

1. O usuário abre o expander `Agente de Orçamento`.
2. `orcamento.py` mantém as mensagens em `st.session_state["mensagens"]`.
3. O prompt é enviado ao `agent` com um `thread_id` fixo.
4. O agente pode chamar `display_budget_metrics`.
5. A resposta final é exibida e adicionada ao histórico.

## Modelo de dados esperado

O código espera, no mínimo, estas tabelas e colunas no Supabase:

### `categorias`

| Coluna | Uso |
| --- | --- |
| `id` | Identificador usado pelos relacionamentos |
| `nome` | Nome exibido nos selects |

### `subcategorias`

| Coluna | Uso |
| --- | --- |
| `id` | Identificador da subcategoria |
| `nome` | Nome exibido nos selects |
| `categoria_id` | Chave da categoria pai |

### `transacoes`

| Coluna | Uso |
| --- | --- |
| `id` | Identificador da transação |
| `data` | Data da movimentação |
| `descricao` | Texto descritivo |
| `valor` | Positivo para receita e negativo para despesa |
| `recorrente` | Indicador booleano |
| `tipo` | `Receita` ou `Despesa` |
| `categoria_id` | Relacionamento com `categorias` |
| `subcategoria_id` | Relacionamento opcional com `subcategorias` |

As relações `categorias(nome)` e `subcategorias(nome)` usadas em `carregar_transacoes()` precisam estar reconhecidas pelo PostgREST/Supabase.

## Configuração do Supabase

Antes de executar a aplicação, confira:

- As tabelas e colunas existem com os nomes esperados.
- As chaves estrangeiras de `transacoes` apontam para as tabelas de classificação.
- A chave usada pela aplicação tem permissão de leitura e escrita necessárias.
- As políticas RLS permitem as operações do usuário técnico da aplicação.
- Os dados de `valor` seguem a regra de sinal documentada.

Ao alterar o schema, atualize primeiro `utils/database.py`, depois os cálculos em `utils/metricas.py` e por fim as telas que exibem as colunas.

## Agente de orçamento

O agente usa o modelo `gpt-4o-mini` com temperatura `0.2`. Seu prompt está em `src/agent.py` e orienta respostas prudentes, com resumo executivo, análise, diagnóstico e recomendações.

A ferramenta atualmente disponível é:

| Ferramenta | Fonte | Finalidade |
| --- | --- | --- |
| `display_budget_metrics` | `utils.metricas.budget_metrics` | Fornecer ao agente saldo, médias, margem de segurança e cash runway |

Ao alterar ferramentas ou o prompt:

1. Mantenha a função da ferramenta pequena e determinística.
2. Não envie chaves ou dados sensíveis para o prompt.
3. Teste o caso sem transações.
4. Teste o caso com despesas e receitas em meses diferentes.
5. Verifique se a resposta não apresenta métricas incompatíveis com o período exibido.

## Relatórios PDF

O módulo `relatorio.py` contém o pipeline:

```text
DataFrame do Supabase
    -> gerar_dados_gerais()
    -> render_slide() com Jinja2
    -> html_to_pdf() com pdfkit/wkhtmltopdf
    -> mont_relatorio() com pypdf
    -> reports/relatorio_<timestamp>.pdf
```

Para usar esse fluxo, instale `wkhtmltopdf`, confirme que `kaleido` consegue exportar imagens Plotly e execute o módulo no diretório raiz:

```bash
uv run python relatorio.py
```

O resultado é salvo em `reports/`, que não possui uma política de retenção implementada no código atual. Não use este fluxo em produção sem revisar o filtro de datas, o tratamento de DataFrame vazio, a origem do DataFrame e a integração de download no Streamlit.

O `PRD.md` descreve uma arquitetura futura com `src/report/builder.py`, `renderer.py` e `assembler.py`. Esses arquivos não existem atualmente; o pipeline real está concentrado em `relatorio.py`.

## Testes e qualidade

### Compilação

```bash
uv run python -m compileall .
```

### Testes

```bash
uv run pytest
```

O `test_app.py` atual verifica um contador (`Valor: 0` para `Valor: 1`) que não existe no `app.py` financeiro. Ele deve ser substituído por testes alinhados ao comportamento atual antes de ser usado como gate de CI.

### Ruff

```bash
uv run ruff check .
```

Para validar apenas arquivos Python rastreados:

```bash
uv run ruff check --force-exclude $(git ls-files "*.py")
```

O projeto não configura regras próprias do Ruff em `pyproject.toml`; a configuração padrão pode sinalizar problemas históricos que precisam ser avaliados antes de aplicar correções automáticas.

## Manutenção

### Checklist para alterações de banco

1. Atualizar o schema e as políticas RLS no Supabase.
2. Atualizar as funções de `utils/database.py`.
3. Conferir o DataFrame produzido por `carregar_transacoes()`.
4. Revisar filtros e agregações em `utils/metricas.py`.
5. Testar cadastro, atualização, exclusão e recarregamento da página.

### Checklist para novas páginas

1. Criar uma função de página em `utils/utils.py` ou um arquivo no padrão das páginas existentes.
2. Adicionar a rota em `app.py`.
3. Definir claramente se a página é pública, autorizada ou administrativa.
4. Reutilizar `inject_global_css()` e os padrões de `st.session_state` existentes.
5. Documentar a página nesta tabela do README.

### Checklist para métricas

1. Definir a regra de negócio e o sinal dos valores.
2. Validar DataFrames vazios e períodos sem registros.
3. Evitar divisão por zero ao calcular médias diárias.
4. Reutilizar `calcular_metricas_orcamento()` quando a métrica também for usada pela IA.
5. Adicionar teste unitário com dados pequenos e determinísticos.

### Checklist antes de publicar

1. Confirmar que `.streamlit/secrets.toml` não está no Git.
2. Executar `pytest`, `ruff check .` e `compileall`.
3. Testar login autorizado e não autorizado.
4. Testar as operações de escrita com dados de teste.
5. Confirmar que os gráficos carregam sem dados e com dados.
6. Conferir logs e mensagens de erro sem expor credenciais.

## Limitações conhecidas

- O módulo `src/report/__init__.py` importa `src.report.builder.construir_relatorio`, mas `builder.py` não está presente no repositório atual. Não use esse import como prova de que a arquitetura do PRD está implementada.
- `relatorio.py` executa consultas e geração de PDF no nível do módulo. Importá-lo em outro módulo pode produzir efeitos colaterais e arquivos.
- `gerar_dados_gerais(dataframe)` recebe um DataFrame, mas usa a variável global `df` para os cálculos. O parâmetro deve ser corrigido antes de reutilizar a função em outros contextos.
- O tratamento de DataFrame vazio em `gerar_dados_gerais()` não inicializa todas as métricas antes do retorno; o fluxo de relatório precisa de teste específico para o caso sem dados.
- O agente usa `InMemorySaver`; o histórico não é persistido entre reinícios e o `thread_id` está fixo em `conversa_teste_1`.
- O teste atual não representa a aplicação financeira.
- Não há migrações SQL ou definição de schema versionada neste repositório; alterações do banco precisam ser controladas no projeto Supabase.
- A lista de categorias de receita/despesa em `show_filtros()` usa IDs fixos. Se os IDs mudarem, os filtros podem classificar categorias incorretamente.
- O cache de `carregar_transacoes()` tem TTL de 60 segundos e pode atrasar a visualização de alterações.

## Segurança

- Nunca commit secrets, tokens OAuth, chaves Supabase ou chaves OpenAI.
- Restrinja o acesso no Supabase com RLS e permissões mínimas.
- Mantenha `emails_autorizados` sob controle administrativo.
- Avalie cuidadosamente qualquer nova ferramenta exposta ao agente, especialmente ferramentas de escrita.
- Trate texto produzido pelo agente como conteúdo não confiável antes de renderizá-lo em HTML ou PDF.

## Licença

Não há arquivo de licença neste repositório. Defina a licença antes de distribuir o projeto fora da organização.
