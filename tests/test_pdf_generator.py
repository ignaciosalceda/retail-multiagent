"""
Tests para el módulo de generación de PDF (src/reports/pdf_generator.py)
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.reports.pdf_generator import markdown_to_pdf


class TestMarkdownToPdf:
    """Tests para la función markdown_to_pdf"""

    def test_markdown_to_pdf_creates_file(self):
        """Verifica que markdown_to_pdf crea un archivo PDF"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_report.pdf")
            markdown_text = "# Test Report\n\nThis is a test."

            result = markdown_to_pdf(markdown_text, output_path)

            assert result == output_path
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0

    def test_markdown_to_pdf_default_filename(self):
        """Verifica que markdown_to_pdf use 'report.pdf' como nombre por defecto"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                markdown_text = "# Test"
                result = markdown_to_pdf(markdown_text)

                assert result == "report.pdf"
                assert os.path.exists("report.pdf")
            finally:
                os.chdir(original_cwd)

    def test_markdown_to_pdf_with_headings(self):
        """Verifica que markdown_to_pdf procese encabezados"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "headings_test.pdf")
            markdown_text = "# Heading 1\n## Heading 2\nContent here\n"

            result = markdown_to_pdf(markdown_text, output_path)

            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0

    def test_markdown_to_pdf_with_multiple_lines(self):
        """Verifica que markdown_to_pdf maneje múltiples líneas"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "multiline_test.pdf")
            markdown_text = (
                "# Reporte de Ventas\n\n"
                "## Resumen Ejecutivo\n"
                "Las ventas aumentaron un 25%.\n\n"
                "## Detalles\n"
                "Línea 1\n"
                "Línea 2\n"
                "Línea 3\n"
            )

            result = markdown_to_pdf(markdown_text, output_path)

            assert os.path.exists(output_path)

    def test_markdown_to_pdf_empty_content(self):
        """Verifica que markdown_to_pdf maneje contenido vacío"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "empty_test.pdf")
            markdown_text = ""

            result = markdown_to_pdf(markdown_text, output_path)

            assert os.path.exists(output_path)

    def test_markdown_to_pdf_with_special_characters(self):
        """Verifica que markdown_to_pdf maneje caracteres especiales"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "special_chars_test.pdf")
            markdown_text = (
                "# Reporte con Caracteres Especiales\n\n"
                "Contenido con números: 123, 456.78\n"
                "Símbolos: €, ©, ®\n"
                "Caracteres acentuados: áéíóú\n"
            )

            result = markdown_to_pdf(markdown_text, output_path)

            assert os.path.exists(output_path)

    def test_markdown_to_pdf_with_tables(self):
        """Verifica que markdown_to_pdf maneje tablas markdown"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "table_test.pdf")
            markdown_text = (
                "# Tabla de Datos\n\n"
                "| Producto | Ventas |\n"
                "| --- | --- |\n"
                "| Producto A | 1000 |\n"
                "| Producto B | 2000 |\n"
            )

            result = markdown_to_pdf(markdown_text, output_path)

            assert os.path.exists(output_path)

    def test_markdown_to_pdf_returns_path(self):
        """Verifica que markdown_to_pdf retorna la ruta del archivo"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.pdf")
            markdown_text = "Test content"

            result = markdown_to_pdf(markdown_text, output_path)

            assert isinstance(result, str)
            assert result == output_path

    def test_markdown_to_pdf_with_long_content(self):
        """Verifica que markdown_to_pdf maneje contenido largo"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "long_content_test.pdf")
            markdown_text = "# Report\n\n" + "\n".join(
                [f"Línea {i}: Contenido del párrafo número {i}" for i in range(100)]
            )

            result = markdown_to_pdf(markdown_text, output_path)

            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0

    def test_markdown_to_pdf_file_not_empty(self):
        """Verifica que el archivo PDF generado no esté vacío"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "nonempty_test.pdf")
            markdown_text = "# Test Report\n\nContent"

            markdown_to_pdf(markdown_text, output_path)

            assert os.path.getsize(output_path) > 100  # Los PDFs tienen cabeceras

    def test_markdown_to_pdf_creates_directory_structure(self):
        """Verifica que markdown_to_pdf funcione con rutas complejas"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Crear directorios anidados
            nested_dir = os.path.join(tmpdir, "reports", "2024", "december")
            os.makedirs(nested_dir, exist_ok=True)
            output_path = os.path.join(nested_dir, "report.pdf")

            markdown_text = "# Nested Report"

            result = markdown_to_pdf(markdown_text, output_path)

            assert os.path.exists(result)
