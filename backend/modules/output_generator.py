"""
Output Generation module.
Generates structured outputs in JSON, CSV, and Excel formats.
"""
import json
import os
import pandas as pd
from typing import Dict, List
from pathlib import Path
from utils.logger import get_logger

logger = get_logger("output_generator")


def generate_json_output(data: Dict, output_path: str) -> str:
    """Generate JSON output file."""
    logger.info(f"Generating JSON output: {output_path}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    logger.info(f"JSON output saved: {output_path}")
    return output_path


def generate_csv_output(data: Dict, output_path: str) -> str:
    """Generate CSV output from extracted data."""
    logger.info(f"Generating CSV output: {output_path}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    rows = []

    # Add document info
    rows.append({
        "category": "document_info",
        "field": "file_name",
        "value": data.get("file_name", ""),
    })
    rows.append({
        "category": "document_info",
        "field": "file_type",
        "value": data.get("file_type", ""),
    })
    rows.append({
        "category": "document_info",
        "field": "classification",
        "value": data.get("classification", {}).get("document_type", ""),
    })

    # Add OCR text
    ocr_data = data.get("ocr_results", {})
    rows.append({
        "category": "ocr",
        "field": "full_text",
        "value": ocr_data.get("full_text", ""),
    })
    rows.append({
        "category": "ocr",
        "field": "confidence",
        "value": str(ocr_data.get("combined_confidence", "")),
    })

    # Add entities
    nlp_data = data.get("nlp_results", {})
    entities = nlp_data.get("entities", {})
    for category, entity_list in entities.items():
        for entity in entity_list:
            rows.append({
                "category": f"entity_{category}",
                "field": entity.get("label", ""),
                "value": entity.get("text", ""),
            })

    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False, encoding="utf-8")

    logger.info(f"CSV output saved: {output_path}")
    return output_path


def generate_excel_output(data: Dict, output_path: str) -> str:
    """Generate Excel output with multiple sheets."""
    logger.info(f"Generating Excel output: {output_path}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        # Sheet 1: Document Info
        info_rows = [
            {"Field": "File Name", "Value": data.get("file_name", "")},
            {"Field": "File Type", "Value": data.get("file_type", "")},
            {"Field": "Document Type", "Value": data.get("classification", {}).get("document_type", "")},
            {"Field": "Confidence", "Value": str(data.get("classification", {}).get("confidence", ""))},
            {"Field": "Processing Time", "Value": str(data.get("processing_time", ""))},
        ]
        pd.DataFrame(info_rows).to_excel(
            writer, sheet_name="Document Info", index=False
        )

        # Sheet 2: Extracted Text
        ocr_data = data.get("ocr_results", {})
        text_rows = [
            {
                "Engine": ocr_data.get("primary_engine", ""),
                "Confidence": ocr_data.get("combined_confidence", ""),
                "Text": ocr_data.get("full_text", ""),
            }
        ]
        pd.DataFrame(text_rows).to_excel(
            writer, sheet_name="Extracted Text", index=False
        )

        # Sheet 3: Entities
        nlp_data = data.get("nlp_results", {})
        entity_rows = []
        entities = nlp_data.get("entities", {})
        for category, entity_list in entities.items():
            for entity in entity_list:
                entity_rows.append({
                    "Category": category,
                    "Label": entity.get("label", ""),
                    "Text": entity.get("text", ""),
                })
        if entity_rows:
            pd.DataFrame(entity_rows).to_excel(
                writer, sheet_name="Entities", index=False
            )

        # Sheet 4+: Tables
        tables = data.get("tables", [])
        for i, table in enumerate(tables):
            table_data = table.get("data", [])
            if table_data:
                df = pd.DataFrame(table_data)
                sheet_name = f"Table {i+1}"
                df.to_excel(writer, sheet_name=sheet_name, index=False)

    logger.info(f"Excel output saved: {output_path}")
    return output_path


def generate_all_outputs(data: Dict, output_dir: str, job_id: str) -> Dict[str, str]:
    """Generate all output formats."""
    logger.info(f"Generating all output formats for job {job_id}")
    os.makedirs(output_dir, exist_ok=True)

    outputs = {}
    outputs["json"] = generate_json_output(
        data, os.path.join(output_dir, f"{job_id}_results.json")
    )
    outputs["csv"] = generate_csv_output(
        data, os.path.join(output_dir, f"{job_id}_results.csv")
    )
    outputs["excel"] = generate_excel_output(
        data, os.path.join(output_dir, f"{job_id}_results.xlsx")
    )

    logger.info(f"All outputs generated: {list(outputs.keys())}")
    return outputs
