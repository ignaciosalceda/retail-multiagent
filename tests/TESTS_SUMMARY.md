# Suite de Tests - Retail Intelligence AI Multiagent System

## Resumen de Ejecución

✅ **62 tests PASADOS** en 6.56 segundos

## Cobertura de Tests

### 1. **Configuración** (`test_config.py`) - 6 tests
- Instantiación de Settings con parámetros válidos
- Generación correcta de URLs de SQLAlchemy
- Manejo de diferentes host/puerto
- Carga de variables de entorno
- Valores por defecto
- Validación de campos requeridos

### 2. **Base de Datos** (`test_db.py`) - 8 tests
- Creación y caching de engine (singleton)
- Ejecución de queries SELECT
- Uso de parámetros en queries
- Resultados vacíos
- Formato de respuesta (lista de dicts)
- Manejo de errores de conexión

### 3. **Herramientas SQL** (`test_sql_tool.py`) - 19 tests

#### Truncamiento de filas:
- Sin truncamiento necesario
- Con truncamiento (>50 filas)
- Listas vacías
- Máximo por defecto

#### Conversión a Markdown:
- Tablas básicas
- Resultados vacíos
- Una sola fila
- Valores faltantes
- Diferentes tipos de datos

#### Query Retail Database:
- Queries SELECT permitidas
- SELECT mayúsculas
- INSERT/DELETE/UPDATE/DROP rechazados
- Manejo de errores de BD
- Formato de respuesta
- Truncamiento a 50 filas
- Caracteres especiales

### 4. **Generación de PDF** (`test_pdf_generator.py`) - 11 tests
- Creación de archivos PDF
- Nombres por defecto
- Procesamiento de encabezados
- Múltiples líneas
- Contenido vacío
- Caracteres especiales (€, ©, acentos)
- Tablas markdown
- Rutas de retorno
- Contenido largo
- Archivos no vacíos
- Estructuras de directorios anidadas

### 5. **Configuración LLM** (`test_llm_config.py`) - 3 tests
- Creación de instancias LLM
- Uso del modelo correcto
- Caching singleton

### 6. **Integración** (`test_integration.py`) - 6 tests
- Router detecta intención SQL
- Router detecta intención docs
- Router hace fallback a 'docs' en errores
- Flujo SQL funciona
- Flujo docs funciona
- GlobalState está correctamente definido

### 7. **Utilidades** (`test_utilities.py`) - 8 tests

#### Validación:
- Queries SQL válidas
- Detección de queries inválidas

#### Formato:
- Manejo de decimales
- Manejo de valores NULL
- Manejo de datetimes

#### Manejo de Errores:
- Errores de conexión
- Timeouts

#### Rendimiento:
- Truncamiento rápido (< 1s)
- Conversión a markdown rápida (< 1s)

## Archivos Creados

```
tests/
├── __init__.py
├── conftest.py                # Configuración global de pytest
├── pytest.ini                 # Configuración de pytest
├── README.md                  # Documentación de tests
├── test_config.py             # Tests de configuración
├── test_db.py                 # Tests de base de datos
├── test_sql_tool.py           # Tests de herramientas SQL
├── test_pdf_generator.py      # Tests de generación de PDF
├── test_llm_config.py         # Tests de configuración LLM
├── test_integration.py        # Tests de integración
└── test_utilities.py          # Tests de utilidades
```

## Cómo Ejecutar

### Ejecutar todos los tests:
```bash
cd /home/ignaciosalcedarodr/langgraph-demo
source .venv/bin/activate
python -m pytest tests/ -v
```

### Ejecutar tests específicos:
```bash
python -m pytest tests/test_config.py -v
python -m pytest tests/test_sql_tool.py::TestQueryRetailDatabase -v
```

### Ejecutar con cobertura:
```bash
python -m pytest tests/ --cov=src --cov-report=html
```

### Ejecutar tests que coincidan con un patrón:
```bash
python -m pytest -k "database" -v
```

## Características Clave

✅ Tests unitarios aislados con mocks  
✅ Tests de integración para flujos principales  
✅ Cobertura de casos normales y excepcionales  
✅ Manejo de caracteres especiales y datos raros  
✅ Validación de seguridad (solo SELECT permitido)  
✅ Tests de rendimiento (< 1 segundo)  
✅ Fixtures reutilizables en conftest.py  
✅ Configuración de pytest optimizada  

## Notas Importantes

- Los tests no requieren la BD real en ejecución (usan mocks cuando es necesario)
- Los tests de BD usan SQLite en memoria para rapidez
- Los tests de LLM mockean ChatOllama
- Todos los tests son independientes y pueden ejecutarse en cualquier orden
- El proyecto usa pytest 9.0.2 con plugins langsmith y Faker
