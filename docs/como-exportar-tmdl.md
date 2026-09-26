# Cómo llevar tu modelo semántico de Power BI a este repositorio

Este repositorio guarda el modelo semántico (tablas, columnas, medidas,
relaciones y parámetros de conexión) como texto plano en formato **TMDL**
(`semantic-model/definition/`). Al ser texto, Git puede versionarlo,
compararlo (diff) y validarlo automáticamente — algo que no es posible con
un `.pbix` binario.

## Opción A: Power BI Desktop con formato de proyecto (.pbip) — recomendada

1. En Power BI Desktop: **Archivo → Opciones y configuración → Opciones →
   Características de vista previa** → activa **"Formato de proyecto de
   Power BI"** (PBIP) y **"Formato de modelo de almacenamiento TMDL"**.
2. Guarda tu archivo como `.pbip` (**Archivo → Guardar como**). Power BI
   generará dos carpetas: `TuProyecto.Report/` y `TuProyecto.SemanticModel/`.
3. Copia el contenido de `TuProyecto.SemanticModel/definition/` dentro de
   `semantic-model/definition/` de este repositorio (reemplaza la carpeta
   `tables/`, `relationships.tmdl`, `model.tmdl`, `expressions.tmdl`, etc.).
4. **No copies credenciales**: los parámetros de conexión (servidor, base
   de datos) van en `expressions.tmdl` como parámetros de consulta; nunca
   subas usuarios/contraseñas ni cadenas de conexión con secretos.
5. Ejecuta las pruebas localmente (ver README) antes de hacer commit.

## Opción B: Tabular Editor 2/3

1. Conecta Tabular Editor al modelo (Power BI Desktop en vivo, o el
   `.pbix` publicado).
2. **File → Save As → Folder (TMDL)** para exportar el modelo como
   carpeta TMDL.
3. Copia el contenido dentro de `semantic-model/definition/` igual que en
   la Opción A.

## Buenas prácticas antes de subir

- Toda medida debe tener `formatString` y una descripción (comentario
  `///` justo encima de la medida). Las pruebas fallan si falta alguna.
- Nombres de tabla/medida únicos (sin duplicados).
- Verifica que las relaciones (`relationships.tmdl`) apunten a tablas y
  columnas que realmente existan.
- No subas archivos `.pbix` completos por defecto (ver `.gitignore`); si
  tu equipo sí los necesita versionados, coordina el tamaño del repo.
