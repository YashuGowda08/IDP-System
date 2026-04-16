"""
Table Extraction module using tabula-py.
Detects and extracts tables from PDFs and converts to DataFrames.
"""
import pandas as pd
import numpy as np
import json
import os
from typing import List, Dict, Optional
from utils.logger import get_logger

logger = get_logger("table_extractor")


def extract_tables_from_pdf(pdf_path: str) -> List[Dict]:
    """
    Extract tables from a PDF using tabula-py.
    Returns list of dicts containing table data and metadata.
    """
    logger.info(f"Extracting tables from PDF: {pdf_path}")
    tables_data = []

    try:
        import tabula

        # Extract all tables
        tables = tabula.read_pdf(
            pdf_path,
            pages="all",
            multiple_tables=True,
            lattice=True,  # Try lattice mode first (bordered tables)
        )

        if not tables:
            logger.info("No lattice tables found, trying stream mode...")
            tables = tabula.read_pdf(
                pdf_path,
                pages="all",
                multiple_tables=True,
                stream=True,  # Stream mode for borderless tables
            )

        for i, table in enumerate(tables):
            if table.empty:
                continue

            # Clean the DataFrame
            table = table.dropna(how="all")
            table = table.dropna(axis=1, how="all")
            table.columns = [
                str(col).strip() for col in table.columns
            ]
            
            # Replace NaN with empty string for JSON compliance
            table = table.fillna("")

            tables_data.append({
                "table_index": i + 1,
                "rows": len(table),
                "columns": len(table.columns),
                "column_names": list(table.columns),
                "data": table.to_dict(orient="records"),
                "html": table.to_html(index=False, classes="extracted-table"),
                "csv": table.to_csv(index=False),
            })

            logger.info(
                f"  Table {i+1}: {len(table)} rows x {len(table.columns)} columns"
            )

        logger.info(f"Extracted {len(tables_data)} tables from PDF")

    except Exception as e:
        logger.error(f"Table extraction from PDF failed: {e}")

    return tables_data


def extract_tables_from_text(text: str) -> List[Dict]:
    """
    Attempt to parse table-like structures from OCR text.
    Used as fallback for image-based documents.
    """
    logger.info("Attempting to extract tables from OCR text...")
    tables_data = []

    lines = text.strip().split("\n")
    potential_table_lines = []
    current_table = []

    for line in lines:
        # Detect table-like lines (containing multiple separators)
        separators = line.count("|") + line.count("\t")
        spaces = len([s for s in line.split("  ") if s.strip()]) - 1

        if separators >= 2 or spaces >= 2:
            current_table.append(line)
        else:
            if len(current_table) >= 2:
                potential_table_lines.append(current_table)
            current_table = []

    if len(current_table) >= 2:
        potential_table_lines.append(current_table)

    for idx, table_lines in enumerate(potential_table_lines):
        try:
            rows = []
            for line in table_lines:
                if "|" in line:
                    cells = [
                        c.strip() for c in line.split("|") if c.strip()
                    ]
                elif "\t" in line:
                    cells = [c.strip() for c in line.split("\t") if c.strip()]
                else:
                    cells = [c.strip() for c in line.split("  ") if c.strip()]

                if cells:
                    rows.append(cells)

            if len(rows) >= 2:
                # First row as header
                max_cols = max(len(row) for row in rows)
                normalized_rows = [
                    row + [""] * (max_cols - len(row)) for row in rows
                ]

                headers = normalized_rows[0]
                data_rows = normalized_rows[1:]

                df = pd.DataFrame(data_rows, columns=headers)
                
                # Replace NaN with empty string for JSON compliance
                df = df.fillna("")

                tables_data.append({
                    "table_index": idx + 1,
                    "rows": len(df),
                    "columns": len(df.columns),
                    "column_names": list(df.columns),
                    "data": df.to_dict(orient="records"),
                    "html": df.to_html(index=False, classes="extracted-table"),
                    "csv": df.to_csv(index=False),
                    "source": "ocr_text",
                })

        except Exception as e:
            logger.warning(f"Failed to parse table from text: {e}")

    logger.info(f"Extracted {len(tables_data)} tables from text")
    return tables_data


def tables_to_dataframes(tables_data: List[Dict]) -> List[pd.DataFrame]:
    """Convert extracted table data back to Pandas DataFrames."""
    dataframes = []
    for table in tables_data:
        df = pd.DataFrame(table["data"])
        dataframes.append(df)
    return dataframes
