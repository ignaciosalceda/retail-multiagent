# Retail Intelligence AI Multiagent System

## Introducción

 Plataforma conversacional avanzada que permite interactuar con datos estructurados y no estructurados del dominio retail mediante lenguaje natural. El sistema orquesta múltiples agentes especializados utilizando LangChain y LangGraph, empleando modelos LLM autoalojados a través de Ollama.

Este proyecto está concebido como una solución integral para entornos de ingeniería de datos donde **convergen la lógica de negocio, la consulta sobre datos estructurados y el análisis documental**. 

Permite generar dinámicamente consultas SQL optimizadas sobre bases de datos relacionales, realizar búsquedas contextuales sobre conocimiento no estructurado y transformar los resultados en informes enriquecidos en PDF. Todo esto posibilita una toma de decisiones más rápida, accesible y basada en evidencia, al permitir a usuarios técnicos y no técnicos interactuar con los datos mediante lenguaje natural en flujos de trabajo reproducibles y auditables.

## Arquitectura del Sistema

El sistema está compuesto por los siguientes agentes:

- **Agente SQL**: Traduce preguntas en lenguaje natural a SQL ejecutable sobre una base de datos Oracle XE, devolviendo resultados estructurados.
- **Agente Documental (RAG)**: Busca y sintetiza información desde documentos vectorizados mediante embeddings (`all-MiniLM-L6-v2`) y devuelve respuestas contextuales. Útil para enlazar lógica relacional de la base de datos con contexto de negocio.
- **Agente de Reportes**: Formatea respuestas complejas en Markdown y las convierte en archivos PDF para entrega profesional.
- **Agente de Ruteo**: Controlador central construido con LangGraph que decide qué agente ejecutar en función de la intención de la pregunta.

## Requisitos

- Python 3.10+
- Docker + Docker Compose
- Oracle XE (imagen `gvenzl/oracle-xe`)
- Ollama (para usar modelos como `mistral` o `llama2`)
- Dependencias de Python (`requirements.txt`)

## Instalación y Puesta en Marcha

```bash
# Clonar el repositorio
git clone https://github.com/tuusuario/retail-intelligence-agent.git
cd retail-intelligence-agent

# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Descargar modelo para Ollama
ollama pull mistral

# Levantar la base de datos
docker-compose up -d

# Poblar la base de datos
python scripts/seed_oracle.py
```

## Ejecución

```bash
# Ejecutar agente SQL
python -m src.experiments.run_sql_graph

# Ejecutar agente documental
python -m src.experiments.run_docs_graph

# Ejecutar grafo con enrutamiento
python -m src.experiments.run_router_graph

# Generar informe PDF a partir de la respuesta
python -m src.experiments.run_report_graph
```

## Ejemplo de Uso

Pregunta: _"¿Cuáles son las categorías con mayor volumen de ventas?"_

Respuesta generada:

```
| nombre   | total_ventas |
|----------|---------------|
| Limpieza | 220326.08 €   |
| Snacks   | 150535.67 €   |
...

La categoría con mayor venta es "Limpieza".
```

## Configuración

- `.env`: credenciales de Oracle, configuración de puerto y host.
- Modelos LLM autoalojados gestionados vía Ollama.
- Documentos vectorizados con `HuggingFaceEmbeddings`.

## Créditos

- [LangChain](https://www.langchain.com/)
- [LangGraph](https://www.langgraph.dev/)
- [Ollama](https://ollama.com/)
- [HuggingFace](https://huggingface.co/)
- [Oracle XE](https://www.oracle.com/database/technologies/xe-downloads.html)

## Licencia

MIT