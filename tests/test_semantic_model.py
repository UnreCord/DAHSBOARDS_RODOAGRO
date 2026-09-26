"""
Pruebas automáticas del modelo semántico (semantic-model/definition).

Se ejecutan en cada push/PR (ver .github/workflows/validate-semantic-model.yml)
para detectar errores de forma temprana, antes de que lleguen a Power BI:
nombres duplicados, relaciones rotas, DAX mal formado, medidas sin
formato/descr, tablas vacías, etc.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import validate_tmdl as v  # noqa: E402


def _tables():
    return v.parse_tables()


def _relationships():
    return v.parse_relationships()


def test_al_menos_una_tabla_definida():
    tables = _tables()
    assert tables, "No se encontró ninguna tabla en semantic-model/definition/tables"


def test_no_hay_tablas_duplicadas():
    duplicadas = v.find_duplicate_table_names(_tables())
    assert not duplicadas, f"Tablas con nombre duplicado: {duplicadas}"


def test_no_hay_medidas_duplicadas():
    duplicadas = v.find_duplicate_measure_names(_tables())
    assert not duplicadas, f"Medidas con nombre duplicado: {duplicadas}"


def test_no_hay_tablas_sin_columnas():
    vacias = v.find_empty_tables(_tables())
    nombres = [t.name for t in vacias]
    assert not vacias, f"Tablas sin columnas definidas: {nombres}"


def test_no_hay_medidas_con_expresion_vacia():
    vacias = v.find_empty_measures(_tables())
    detalle = [f"{m.file}:{m.line} {m.name}" for m in vacias]
    assert not vacias, f"Medidas sin expresión DAX: {detalle}"


def test_expresiones_dax_balanceadas():
    rotas = v.find_unbalanced_measures(_tables())
    detalle = [f"{m.file}:{m.line} {m.name} -> {m.expression}" for m in rotas]
    assert not rotas, (
        "Medidas con paréntesis/corchetes/llaves sin balancear "
        f"(revisar antes de abrir en Power BI): {detalle}"
    )


def test_medidas_tienen_formato_numerico():
    sin_formato = v.find_measures_without_format_string(_tables())
    detalle = [f"{m.file}:{m.line} {m.name}" for m in sin_formato]
    assert not sin_formato, (
        f"Medidas sin formatString definido (se verán sin formato en el reporte): {detalle}"
    )


def test_medidas_tienen_descripcion():
    sin_descripcion = v.find_measures_without_description(_tables())
    detalle = [f"{m.file}:{m.line} {m.name}" for m in sin_descripcion]
    assert not sin_descripcion, (
        "Medidas sin descripción (agregar comentario '///' encima de la medida): "
        f"{detalle}"
    )


def test_relaciones_apuntan_a_tablas_y_columnas_existentes():
    problemas = v.find_broken_relationships(_tables(), _relationships())
    assert not problemas, "Relaciones rotas encontradas:\n" + "\n".join(problemas)
