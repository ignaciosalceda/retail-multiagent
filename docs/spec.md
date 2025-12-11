# Retail Data Copilot – Especificación funcional

## 1. Descripción general

Retail Data Copilot es un agente conversacional que ayuda a analizar datos de ventas de una empresa retail, consultar documentación interna y ejecutar simulaciones de negocio.

El sistema combina:
- Consultas a una **base de datos relacional** (ventas, tiendas, productos, clientes).
- Búsqueda semántica sobre **documentación interna** (RAG).
- Llamadas a una **API de simulaciones** (p. ej. impacto de descuentos).

El objetivo es que un usuario no técnico pueda hacer preguntas en lenguaje natural y el agente:
1. Decida qué herramientas usar (SQL, RAG, API).
2. Ejecute las acciones necesarias.
3. Devuelva una respuesta clara, justificada y trazable.

---

## 2. Personas usuarias

1. **Analista de negocio**
   - Quiere explorar KPIs sin escribir SQL.
   - Necesita comparativas temporales, por categoría, tienda, región, etc.

2. **Manager / Director de tienda**
   - Quiere entender por qué ciertas métricas suben o bajan.
   - Quiere explicaciones en lenguaje simple.

3. **Data-savvy user (perfil técnico ligero)**
   - Puede entender términos como “margen”, “cohorte”, “segmentación”.
   - Valora poder ver también el SQL generado o los datos brutos.

---

## 3. Alcance funcional

### 3.1. Consultas a la base de datos (SQL)

El agente debe ser capaz de:

1. Obtener métricas básicas:
   - Ventas totales en un período.
   - Ventas por categoría, tienda, región, cliente.
   - Número de transacciones, ticket medio, etc.

2. Comparar períodos:
   - “Última semana vs semana anterior”
   - “Último mes vs mismo mes del año pasado”

3. Filtrar por dimensiones:
   - Por tienda, región, categoría de producto, segmento de cliente, canal de venta.

4. Mostrar resultados:
   - Resumen textual en lenguaje natural.
   - Tabla resumida (pocas filas/columnas) en texto estructurado.

### 3.2. Consultas a documentación (RAG)

El agente debe ser capaz de:

1. Explicar definiciones de KPIs:
   - Ej: “¿Qué significa cliente activo en esta empresa?”
   - Ej: “¿Cómo se calcula el margen bruto?”

2. Recuperar políticas de negocio:
   - Ej: “¿Cuál es la política de devoluciones?”
   - Ej: “¿Cómo se segmentan los clientes?”

3. Referenciar la fuente:
   - Incluir fragmentos relevantes del documento.
   - Indicar de qué documento viene la información.

### 3.3. Acciones / simulaciones vía API

El agente debe ser capaz de:

1. Lanzar simulaciones de descuentos:
   - Ej: “Simula aplicar un 10% de descuento a la categoría Bebidas el próximo mes.”
   - Devolver:
     - Cambio estimado en ventas.
     - Impacto en margen.

2. Simular escenarios simples:
   - “¿Qué pasaría si aumento precios un 5% en esta categoría?”
   - “¿Qué pasaría si incremento el tráfico un 15% en esta tienda?”

*(Las simulaciones pueden basarse en reglas simples y datos históricos; no es necesario un modelo estadístico complejo en esta primera versión.)*

---

## 4. Fuentes de datos y herramientas

### 4.1. Base de datos relacional (MySQL)

Tablas esperadas (aproximadas, adaptar a tu modelo real):

- `regiones`
- `tiendas`
- `empleados`
- `productos`
- `stock_tienda`
- `ventas`
- `clientes` (si existe)

La herramienta SQL debe:
- Generar SQL a partir de lenguaje natural.
- Ejecutar la consulta.
- Manejar errores típicos (tabla/columna no encontrada, sintaxis, etc.).

### 4.2. Documentos para RAG

Ubicación: `docs/raw/`

Tipos de documentos:
- Manual de KPIs.
- Diccionario de datos.
- Políticas de negocio (devoluciones, descuentos, segmentación).
- Descripción de productos/categorías (opcional).

Pipeline:
- Carga → chunking → embeddings → vectorstore.
- Exponer un `retriever` para el agente.

### 4.3. API de simulación

Se expondrá como:
- FastAPI local (por ejemplo en `/simulate/discount` y `/simulate/price_change`),
  o
- Funciones Python que simulan el comportamiento (para desarrollo local).

La herramienta del agente debe poder:
- Recibir parámetros estructurados (categoría, porcentaje, período).
- Devolver un JSON con resultados y explicación.

---

## 5. Comportamiento del agente (vista de alto nivel)

1. El usuario hace una pregunta en lenguaje natural.
2. El agente pasa por un **router de intención** que clasifica en:
   - `sql_query`
   - `rag_docs`
   - `api_simulation`
   - `mixed` (si requiere más de una cosa)
3. Según la intención:
   - Llama al **agente SQL**, **agente RAG** o **agente API**.
4. Un **supervisor**:
   - Revisa los resultados.
   - Los combina si hace falta (ej: contexto RAG + números de SQL).
   - Genera la respuesta final en lenguaje natural.

---

## 6. User stories

1. *Como analista*, quiero preguntar por las ventas totales de la última semana para tener una visión rápida del rendimiento reciente.
2. *Como analista*, quiero obtener las ventas por categoría y tienda en un rango de fechas para identificar qué combinación tienda–categoría funciona mejor.
3. *Como manager*, quiero comparar las ventas de este mes con el mismo mes del año pasado para evaluar el crecimiento.
4. *Como manager*, quiero que el sistema me explique qué significa “cliente activo” para entender mejor los reportes.
5. *Como analista*, quiero saber cómo se calcula el margen bruto para interpretar correctamente los KPIs.
6. *Como manager*, quiero simular un 10% de descuento en una categoría concreta y ver el impacto estimado en ventas y margen antes de tomar la decisión.
7. *Como usuario*, quiero poder encadenar preguntas (follow-ups) sin repetir el contexto, para mantener conversaciones fluidas.
8. *Como usuario*, quiero que el agente me indique cuando no tiene suficiente información para responder con seguridad.

---

## 7. Ejemplos de preguntas de usuario

- “¿Cuáles fueron las ventas totales de la última semana?”
- “Dame las ventas por categoría y tienda en marzo de 2024.”
- “Compárame las ventas de enero de 2024 con enero de 2023 por región.”
- “Explícame cómo se define un cliente activo en esta empresa.”
- “¿Cuál es la política de devoluciones para compras online?”
- “Simula aplicar un 15% de descuento en la categoría Bebidas el próximo mes y dime el impacto estimado.”
- “Y si en vez de 15% fuera 5%, ¿qué pasaría?” (follow-up)

---

## 8. Criterios de aceptación (versión inicial)

1. El agente es capaz de:
   - Responder correctamente al menos un 70% de las consultas SQL sencillas (ventas totales, por categoría, por tienda).
   - Recuperar y citar correctamente fragmentos de documentación relevante para preguntas de RAG.
   - Ejecutar al menos una simulación de descuento mediante la API y devolver una explicación coherente.

2. El sistema:
   - Maneja errores de SQL mostrando un mensaje entendible para el usuario.
   - Indica explícitamente cuando la información no está disponible o es insuficiente.
   - Mantiene el contexto de conversación durante varios turnos.

3. El proyecto incluye:
   - Este documento de especificación.
   - Código organizado en módulos (data, tools, graph, server, eval).
   - Un script o interfaz (CLI o web) para interactuar con el agente.
