# Tests del Proyecto

Suite completa de tests para el proyecto Retail Intelligence AI Multiagent System.

## Estructura de Tests

### `test_config.py`
Tests para el módulo de configuración (`src/config/settings.py`):
- Instantiación de Settings
- Generación de URLs de SQLAlchemy
- Carga de variables de entorno
- Valores por defecto

### `test_db.py`
Tests para el módulo de base de datos (`src/data/db.py`):
- Creación y caching de engine
- Ejecución de queries SELECT
- Uso de parámetros
- Manejo de errores

### `test_sql_tool.py`
Tests para las herramientas SQL (`src/tools/sql_tool.py`):
- Truncamiento de filas
- Conversión a markdown
- Validación de queries (solo SELECT permitido)
- Manejo de datos especiales
- Formato de respuestas

### `test_pdf_generator.py`
Tests para generación de PDF (`src/reports/pdf_generator.py`):
- Creación de archivos PDF
- Procesamiento de markdown
- Manejo de caracteres especiales
- Contenido largo

### `test_llm_config.py`
Tests para configuración del LLM (`src/config/llm.py`):
- Creación de instancias LLM
- Configuración de modelo
- Caching singleton

### `test_integration.py`
Tests de integración para flujos principales:
- Router graph
- Flujo SQL
- Flujo de documentos
- Master graph

### `conftest.py`
Configuración global de pytest con fixtures reutilizables:
- `test_db_url`: URL de base de datos en memoria
- `mock_settings`: Settings mockeados
- `mock_llm`: LLM mockeado

## Ejecución de Tests

### Ejecutar todos los tests
```bash
pytest
```

### Ejecutar tests de un módulo específico
```bash
pytest tests/test_config.py
pytest tests/test_db.py
pytest tests/test_sql_tool.py
```

### Ejecutar con cobertura
```bash
pytest --cov=src --cov-report=html
```

### Ejecutar solo tests que coincidan con un patrón
```bash
pytest -k "test_query" -v
```

### Ejecutar con output detallado
```bash
pytest -v --tb=short
```

## Coverage

Para generar un reporte de cobertura:

```bash
pytest --cov=src --cov-report=term-missing
pytest --cov=src --cov-report=html  # Genera archivo HTML
```

## Requisitos

Los tests requieren los siguientes paquetes:
- `pytest`
- `pytest-cov` (para cobertura)
- Todos los paquetes del `requirements.txt` del proyecto

## Notas

- Los tests de base de datos utilizan SQLite en memoria para evitar dependencias externas
- Los tests de LLM mockean `ChatOllama` para evitar requerir Ollama ejecutándose
- Los tests usan fixtures de `conftest.py` para compartir configuración común
- Se pueden ejecutar sin necesidad de Docker o bases de datos reales
