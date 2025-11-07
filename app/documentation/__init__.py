"""Ferramentas para acessar a biblioteca de documentação do sistema Sol Maior.

Este pacote expõe utilidades em Python para consumir os arquivos Markdown
armazenados na pasta ``docs/``. Ele pode ser utilizado dentro das rotas, tarefas
ou serviços para exibir ou exportar a documentação diretamente do backend.

Funções principais
------------------
- ``get_document(key)``: retorna o conteúdo Markdown completo de um documento.
- ``list_sections(parent=None)``: lista seções disponíveis em determinado nível.
- ``get_tree()``: devolve representação hierárquica da biblioteca.
- ``search_titles(query)``: busca por títulos contendo o termo informado.

Exemplo rápido::

    from app.documentation import get_document, list_sections

    for key, title in list_sections():
        print(key, title)

    markdown = get_document("user-guides/student")
    print(markdown[:200])

A estrutura completa dos caminhos encontra-se em ``registry.py``.
"""

from .registry import (
    DocumentationError,
    get_document,
    get_tree,
    list_sections,
    search_titles,
)

__all__ = [
    "DocumentationError",
    "get_document",
    "get_tree",
    "list_sections",
    "search_titles",
]
