# Convenciones del modelo semántico

- **Tablas**: nombre en singular o plural consistente con el negocio (ej.
  `Ventas`, `Productos`, `Clientes`, `Calendario`).
- **Medidas**: nombre descriptivo con mayúscula inicial por palabra
  (`Total Ventas`, `Cantidad de Ventas`). Toda medida debe llevar:
  - Comentario de documentación `///` inmediatamente encima.
  - `formatString` explícito.
- **Columnas**: usar el nombre de origen tal cual viene de la fuente,
  salvo que requiera traducción/legibilidad para el usuario final.
- **Relaciones**: siempre declaradas en `relationships.tmdl`, nunca solo
  "a mano" dentro de Power BI Desktop sin exportar.
- **Parámetros de conexión**: van en `expressions.tmdl` como parámetros de
  consulta (`Servidor`, `BaseDeDatos`, etc.). Nunca incluir usuario,
  contraseña ni cadenas de conexión completas con secretos en el
  repositorio.
- **Un modelo semántico reutilizable**: la idea de este repo es que cada
  nuevo proyecto de Power BI parta de `semantic-model/` como base (tablas,
  medidas y relaciones ya probadas), en lugar de reconstruir todo desde
  cero.
