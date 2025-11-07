"""Catálogo centralizado dos documentos de referência do sistema Sol Maior.

Este módulo oferece utilidades para consumir os arquivos Markdown disponíveis na
pasta ``docs/`` e expô-los como uma biblioteca Python. Ele mantém um índice
hierárquico das seções e fornece funções de leitura, listagem e busca.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

__all__ = [
    "DocumentationError",
    "DocumentEntry",
    "get_document",
    "get_tree",
    "iter_documents",
    "list_sections",
    "search_titles",
]


class DocumentationError(RuntimeError):
    """Erro lançado quando um documento solicitado não está disponível."""


@dataclass(frozen=True)
class DocumentEntry:
    """Representa uma seção/documento da biblioteca."""

    key: str
    title: str
    path: Optional[Path]
    description: Optional[str]
    children: Tuple[str, ...]

    def to_dict(self) -> Dict[str, Optional[str]]:
        """Retorna representação simples usada pelo ``get_tree``."""

        return {
            "key": self.key,
            "title": self.title,
            "description": self.description,
            "path": str(self.path) if self.path else None,
        }


# Diretório raíz dos arquivos Markdown
DOCS_ROOT = Path(__file__).resolve().parents[2] / "docs"

# Estrutura declarativa da biblioteca.
# As chaves representam slugs de acesso; os valores contêm metadados e filhos.
DOCUMENT_TREE: Dict[str, Dict] = {
    "": {
        "title": "Biblioteca de Documentação do Sistema Sol Maior",
        "description": "Índice principal da documentação em Markdown.",
        "path": "README.md",
        "children": {
            "overview": {
                "title": "Visão Geral do Sistema",
                "path": "overview/overview.md",
            },
            "user-guides": {
                "title": "Guias por Tipo de Usuário",
                "description": "Manuais dedicados para alunos, professores, secretaria e administradores.",
                "children": {
                    "student": {
                        "title": "Manual do Aluno",
                        "path": "user-guides/student.md",
                    },
                    "teacher": {
                        "title": "Manual do Professor",
                        "path": "user-guides/teacher.md",
                    },
                    "secretary": {
                        "title": "Manual da Secretaria",
                        "path": "user-guides/secretary.md",
                    },
                    "admin": {
                        "title": "Manual do Administrador",
                        "path": "user-guides/admin.md",
                    },
                },
            },
            "modules": {
                "title": "Documentação dos Módulos",
                "description": "Objetivos, permissões e fluxos de cada módulo do sistema.",
                "children": {
                    "academic": {
                        "title": "Módulo Acadêmico",
                        "path": "modules/academic.md",
                    },
                    "scheduling": {
                        "title": "Módulo Agenda (Scheduling)",
                        "path": "modules/scheduling.md",
                    },
                    "finance": {
                        "title": "Módulo Financeiro",
                        "path": "modules/finance.md",
                    },
                    "recitals": {
                        "title": "Módulo de Recitais & Performances",
                        "path": "modules/recitals.md",
                    },
                    "landing-page": {
                        "title": "Módulo Landing Page & Marketing",
                        "path": "modules/landing_page.md",
                    },
                    "settings": {
                        "title": "Módulo Configurações & Administração",
                        "path": "modules/settings.md",
                    },
                    "reports": {
                        "title": "Módulo de Relatórios & Indicadores",
                        "path": "modules/reports.md",
                    },
                    "communications": {
                        "title": "Módulo de Comunicações & Notificações",
                        "path": "modules/communications.md",
                    },
                },
            },
            "glossary": {
                "title": "Glossário de Termos",
                "path": "glossary.md",
            },
            "faq": {
                "title": "Perguntas Frequentes (FAQ)",
                "path": "faq.md",
            },
            "updates": {
                "title": "Registro de Atualizações",
                "path": "updates.md",
            },
        },
    }
}

# Índice flatten para acesso rápido
_INDEX: Dict[str, DocumentEntry] = {}


def _register_tree() -> None:
    """Processa ``DOCUMENT_TREE`` e popula ``_INDEX``."""

    def _register_node(node_key: str, node: Dict) -> None:
        raw_children = node.get("children", {})
        child_keys: List[str] = []

        for child_slug, child in raw_children.items():
            full_child_key = f"{node_key}/{child_slug}" if node_key else child_slug
            child_keys.append(full_child_key)

        path_value = node.get("path")
        path_obj: Optional[Path]
        if path_value is None:
            path_obj = None
        else:
            path_obj = DOCS_ROOT / path_value
            if not path_obj.exists():
                raise DocumentationError(
                    f"Documento '{path_value}' não encontrado em {DOCS_ROOT}."
                )

        entry = DocumentEntry(
            key=node_key,
            title=node["title"],
            path=path_obj,
            description=node.get("description"),
            children=tuple(child_keys),
        )

        _INDEX[node_key] = entry

        for child_slug, child in raw_children.items():
            full_child_key = f"{node_key}/{child_slug}" if node_key else child_slug
            _register_node(full_child_key, child)

    _register_node("", DOCUMENT_TREE[""])


_register_tree()


def list_sections(parent: Optional[str] = None) -> List[Tuple[str, str]]:
    """Retorna lista de pares ``(key, título)`` dos filhos de ``parent``.

    Args:
        parent: chave da seção pai. Use ``None`` (padrão) para o nível raiz.

    Raises:
        DocumentationError: se a chave informada não existir ou não possuir filhos.
    """

    parent_key = parent or ""
    entry = _INDEX.get(parent_key)
    if entry is None:
        raise DocumentationError(f"Seção '{parent_key}' não encontrada na biblioteca.")

    return [(child_key, _INDEX[child_key].title) for child_key in entry.children]


def get_document(key: str = "") -> str:
    """Retorna o conteúdo Markdown bruto associado à ``key``.

    Args:
        key: identificador do documento (ex.: ``"modules/finance"``).

    Raises:
        DocumentationError: se a chave não existir ou não houver arquivo associado.
    """

    entry = _INDEX.get(key)
    if entry is None:
        raise DocumentationError(f"Documento '{key}' não encontrado.")

    if entry.path is None:
        raise DocumentationError(
            f"A seção '{key or 'raiz'}' não possui documento associado."
        )

    try:
        return entry.path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise DocumentationError(
            f"Arquivo '{entry.path}' não pôde ser lido: {exc.strerror}"
        ) from exc


def get_tree() -> Dict[str, object]:
    """Retorna a estrutura hierárquica completa da biblioteca."""

    def _build_node(key: str) -> Dict[str, object]:
        entry = _INDEX[key]
        node_dict = entry.to_dict()
        node_dict["children"] = [_build_node(child) for child in entry.children]
        return node_dict

    return _build_node("")


def search_titles(query: str) -> List[Tuple[str, str]]:
    """Busca títulos que contenham ``query`` (case-insensitive)."""

    normalized = query.strip().lower()
    if not normalized:
        return []

    results: List[Tuple[str, str]] = []
    for key, entry in _INDEX.items():
        if entry.title.lower().find(normalized) != -1:
            results.append((key, entry.title))

    return results


def iter_documents(include_sections_without_file: bool = False) -> Iterator[Tuple[str, DocumentEntry]]:
    """Itera sobre todos os registros do catálogo.

    Args:
        include_sections_without_file: se ``True``, inclui nós que não possuem
            arquivo associado (apenas metadados da seção).
    """

    for key, entry in _INDEX.items():
        if entry.path is None and not include_sections_without_file:
            continue
        yield key, entry
