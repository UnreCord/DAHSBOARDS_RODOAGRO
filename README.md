# Dashboards Agro

Repositorio central del modelo semántico de Power BI (tablas, medidas,
relaciones y parámetros de conexión), pensado como punto de partida
reutilizable para nuevos proyectos de Power BI.

## Estructura

```
semantic-model/definition/   # Modelo semántico en TMDL (texto, versionable)
  database.tmdl               # Nivel de compatibilidad de la base de datos tabular
  model.tmdl                  # Configuración general del modelo
  expressions.tmdl            # Parámetros de conexión (servidor, base de datos, etc.)
  relationships.tmdl          # Relaciones entre tablas
  tables/*.tmdl                # Una tabla por archivo: columnas + medidas

scripts/validate_tmdl.py     # Parser/validador de los archivos TMDL
tests/test_semantic_model.py # Pruebas automáticas (pytest)
.github/workflows/           # CI: corre las pruebas en cada push/PR
docs/                        # Cómo exportar el modelo desde Power BI, convenciones
```

## Cómo subir tu modelo semántico

Ver [`docs/como-exportar-tmdl.md`](docs/como-exportar-tmdl.md) para el
paso a paso (Power BI Desktop con formato `.pbip`/TMDL, o Tabular Editor).

## Pruebas automáticas

Para evitar errores que solo se detectan al abrir el modelo en Power BI
(medidas mal escritas, relaciones rotas, nombres duplicados, etc.), este
repo corre pruebas automáticas en cada push/PR vía GitHub Actions.

Para correrlas localmente:

```bash
pip install -r requirements.txt
pytest tests/ -v
```

Las reglas validadas hoy: tablas/medidas duplicadas, tablas sin columnas,
medidas con expresión DAX vacía o mal balanceada (paréntesis/corchetes),
medidas sin `formatString` o sin descripción, y relaciones que apuntan a
tablas/columnas inexistentes. Ver [`docs/convenciones.md`](docs/convenciones.md)
para el detalle de convenciones.