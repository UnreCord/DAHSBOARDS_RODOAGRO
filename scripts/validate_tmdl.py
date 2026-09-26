"""
Validador de archivos TMDL (Tabular Model Definition Language) del modelo
semántico de Power BI almacenado en semantic-model/definition.

No requiere Power BI ni Tabular Editor: parsea el texto TMDL con
expresiones regulares y aplica reglas básicas para detectar errores
comunes ANTES de abrir el modelo en Power BI (nombres duplicados,
referencias rotas, expresiones DAX mal balanceadas, medidas sin
formato/descr, tablas vacías, etc.).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFINITION_DIR = REPO_ROOT / "semantic-model" / "definition"
TABLES_DIR = DEFINITION_DIR / "tables"
RELATIONSHIPS_FILE = DEFINITION_DIR / "relationships.tmdl"

TABLE_RE = re.compile(r"^table\s+(?:'([^']+)'|(\S+))\s*$")
COLUMN_RE = re.compile(r"^\tcolumn\s+(?:'([^']+)'|(\S+))\s*$")
MEASURE_RE = re.compile(r"^\tmeasure\s+(?:'([^']+)'|(\S+))\s*=\s*(.*)$")
PROP_RE = re.compile(r"^\t\t(\w+):\s*(.*)$")
DOC_COMMENT_RE = re.compile(r"^\t///\s?(.*)$")
RELATIONSHIP_COLUMN_RE = re.compile(
    r"^\t(fromColumn|toColumn):\s*(.+?)\.(.+)$"
)


@dataclass
class Measure:
    name: str
    expression: str
    file: str
    line: int
    format_string: str | None = None
    description: str | None = None


@dataclass
class Column:
    name: str
    file: str
    line: int


@dataclass
class Table:
    name: str
    file: str
    line: int
    columns: list[Column] = field(default_factory=list)
    measures: list[Measure] = field(default_factory=list)


@dataclass
class Relationship:
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    file: str
    line: int


class TmdlValidationError(Exception):
    """Se agrupan todos los errores encontrados en una sola excepción."""


def _expr_is_balanced(expr: str) -> bool:
    pairs = {")": "(", "]": "[", "}": "{"}
    stack: list[str] = []
    for ch in expr:
        if ch in "([{":
            stack.append(ch)
        elif ch in ")]}":
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
    return not stack


def parse_tables(tables_dir: Path = TABLES_DIR) -> list[Table]:
    tables: list[Table] = []
    if not tables_dir.exists():
        return tables

    for tmdl_file in sorted(tables_dir.glob("*.tmdl")):
        lines = tmdl_file.read_text(encoding="utf-8").splitlines()
        current_table: Table | None = None
        pending_doc: list[str] = []
        i = 0
        while i < len(lines):
            line = lines[i]

            table_match = TABLE_RE.match(line)
            if table_match:
                name = table_match.group(1) or table_match.group(2)
                current_table = Table(name=name, file=tmdl_file.name, line=i + 1)
                tables.append(current_table)
                pending_doc = []
                i += 1
                continue

            doc_match = DOC_COMMENT_RE.match(line)
            if doc_match:
                pending_doc.append(doc_match.group(1).strip())
                i += 1
                continue

            column_match = COLUMN_RE.match(line)
            if column_match and current_table is not None:
                name = column_match.group(1) or column_match.group(2)
                current_table.columns.append(
                    Column(name=name, file=tmdl_file.name, line=i + 1)
                )
                pending_doc = []
                i += 1
                continue

            measure_match = MEASURE_RE.match(line)
            if measure_match and current_table is not None:
                name = measure_match.group(1) or measure_match.group(2)
                expr_parts = [measure_match.group(3).strip()]
                measure_line = i + 1
                j = i + 1
                # Captura líneas de continuación de la expresión DAX
                # (indentadas más profundo y sin ser una propiedad conocida).
                while j < len(lines):
                    nxt = lines[j]
                    if PROP_RE.match(nxt):
                        break
                    if TABLE_RE.match(nxt) or COLUMN_RE.match(nxt) or MEASURE_RE.match(nxt):
                        break
                    if nxt.strip() == "":
                        j += 1
                        continue
                    expr_parts.append(nxt.strip())
                    j += 1

                measure = Measure(
                    name=name,
                    expression=" ".join(p for p in expr_parts if p and p != "```"),
                    file=tmdl_file.name,
                    line=measure_line,
                    description="\n".join(pending_doc) if pending_doc else None,
                )
                pending_doc = []

                # Lee propiedades (formatString, description, etc.) que siguen.
                while j < len(lines):
                    prop_match = PROP_RE.match(lines[j])
                    if not prop_match:
                        break
                    key, value = prop_match.group(1), prop_match.group(2).strip().strip('"')
                    if key == "formatString":
                        measure.format_string = value
                    elif key == "description":
                        measure.description = value
                    j += 1

                current_table.measures.append(measure)
                i = j
                continue

            i += 1

    return tables


def parse_relationships(path: Path = RELATIONSHIPS_FILE) -> list[Relationship]:
    if not path.exists():
        return []

    relationships: list[Relationship] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    pending: dict[str, tuple[str, str]] = {}
    start_line = 0
    for idx, line in enumerate(lines):
        if line.startswith("relationship "):
            if pending.get("fromColumn") and pending.get("toColumn"):
                (ft, fc), (tt, tc) = pending["fromColumn"], pending["toColumn"]
                relationships.append(Relationship(ft, fc, tt, tc, path.name, start_line + 1))
            pending = {}
            start_line = idx
            continue
        match = RELATIONSHIP_COLUMN_RE.match(line)
        if match:
            key, table, column = match.group(1), match.group(2), match.group(3)
            pending[key] = (table, column)

    if pending.get("fromColumn") and pending.get("toColumn"):
        (ft, fc), (tt, tc) = pending["fromColumn"], pending["toColumn"]
        relationships.append(Relationship(ft, fc, tt, tc, path.name, start_line + 1))

    return relationships


def find_duplicate_table_names(tables: list[Table]) -> list[str]:
    seen: dict[str, int] = {}
    duplicates = []
    for t in tables:
        seen[t.name] = seen.get(t.name, 0) + 1
    for name, count in seen.items():
        if count > 1:
            duplicates.append(name)
    return duplicates


def find_duplicate_measure_names(tables: list[Table]) -> list[str]:
    seen: dict[str, int] = {}
    for t in tables:
        for m in t.measures:
            seen[m.name] = seen.get(m.name, 0) + 1
    return [name for name, count in seen.items() if count > 1]


def find_unbalanced_measures(tables: list[Table]) -> list[Measure]:
    return [
        m
        for t in tables
        for m in t.measures
        if not _expr_is_balanced(m.expression)
    ]


def find_empty_measures(tables: list[Table]) -> list[Measure]:
    return [m for t in tables for m in t.measures if not m.expression.strip()]


def find_empty_tables(tables: list[Table]) -> list[Table]:
    return [t for t in tables if not t.columns]


def find_measures_without_format_string(tables: list[Table]) -> list[Measure]:
    return [m for t in tables for m in t.measures if not m.format_string]


def find_measures_without_description(tables: list[Table]) -> list[Measure]:
    return [m for t in tables for m in t.measures if not m.description]


def find_broken_relationships(
    tables: list[Table], relationships: list[Relationship]
) -> list[str]:
    tables_by_name = {t.name: {c.name for c in t.columns} for t in tables}
    problems = []
    for r in relationships:
        for table_name, column_name, side in (
            (r.from_table, r.from_column, "fromColumn"),
            (r.to_table, r.to_column, "toColumn"),
        ):
            if table_name not in tables_by_name:
                problems.append(
                    f"{r.file}:{r.line} -> la tabla '{table_name}' referenciada en "
                    f"{side} no existe"
                )
            elif column_name not in tables_by_name[table_name]:
                problems.append(
                    f"{r.file}:{r.line} -> la columna '{table_name}.{column_name}' "
                    f"referenciada en {side} no existe"
                )
    return problems
