# Biblioteca Python de Documentação

Este pacote (`app.documentation`) permite consumir a biblioteca de documentação em Markdown diretamente a partir do backend Python.

## Recursos disponíveis
- `list_sections(parent=None)`: lista seções e sub-seções disponíveis.
- `get_document(key)`: retorna o conteúdo Markdown bruto do documento.
- `get_tree()`: devolve o índice completo em formato de dicionário.
- `search_titles(query)`: busca títulos contendo o termo informado.
- `iter_documents(include_sections_without_file=False)`: itera sobre todos os registros registrados.

## Exemplos de uso

```python
from app.documentation import (
    get_document,
    get_tree,
    iter_documents,
    list_sections,
    search_titles,
)

# Listar seções raiz
for key, title in list_sections():
    print(key, title)

# Obter conteúdo do manual do aluno
student_markdown = get_document("user-guides/student")

# Buscar seções por palavra-chave
results = search_titles("financeiro")

# Navegar pelo índice completo
full_tree = get_tree()

# Iterar sobre todos os documentos disponíveis
for key, entry in iter_documents():
    print(key, entry.title)
```

## Integração sugerida
- **Rotas Flask**: retornar os documentos em endpoints públicos ou administrativos.
- **Painéis internos**: renderizar Markdown em páginas HTML usando bibliotecas como `markdown` ou `markdown2`.
- **CLI/Admin**: gerar PDFs ou enviar trechos de documentação por email a partir de tarefas Celery.

## Estrutura dos caminhos
As chaves utilizadas pelas funções correspondem ao caminho relativo definido em `registry.py`. Exemplos:

| Key | Arquivo |
|-----|---------|
| `""` | `docs/README.md` |
| `"overview"` | `docs/overview/overview.md` |
| `"user-guides/student"` | `docs/user-guides/student.md` |
| `"modules/finance"` | `docs/modules/finance.md` |

Caso novos documentos sejam adicionados, atualize a estrutura `DOCUMENT_TREE` no arquivo `registry.py`.
