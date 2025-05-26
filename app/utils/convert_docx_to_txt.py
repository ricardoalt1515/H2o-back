# Nuevo archivo: convert_docx_to_txt.py
import docx
import os
import re


def convert_docx_to_formatted_txt(docx_path, txt_path):
    """Convierte un archivo DOCX a TXT preservando el formato crítico"""
    doc = docx.Document(docx_path)

    formatted_text = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            formatted_text.append("")  # Línea en blanco
            continue

        # Preservar listas con viñetas
        if text.startswith("*") or text.startswith("-") or re.match(r"^\d+\.", text):
            formatted_text.append(text)
        else:
            formatted_text.append(text)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(formatted_text))


if __name__ == "__main__":
    convert_docx_to_formatted_txt(
        "CUESTIONARIO COMPLETO (2).docx", "app/prompts/cuestionario.txt"
    )
