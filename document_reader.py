"""Read supported documents and prepare their content for speech."""

import argparse
import os
import sys

import pdfplumber

from line_joiner import clean_pdf_text_structure
from markdown_speech import parse_markdown_tables

SUPPORTED_EXTENSIONS = {".md", ".pdf", ".txt"}


def read_document_text(filepath: str) -> str:
    """Read a Markdown, PDF, or plain-text document as raw text."""
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Không tìm thấy file đầu vào: {filepath}")

    extension = os.path.splitext(filepath)[1].lower()
    if extension not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValueError(f"Chỉ hỗ trợ các định dạng: {supported}")

    if extension == ".pdf":
        text = _read_pdf_text(filepath)
    else:
        text = _read_text_file(filepath)

    text = text.strip()
    if not text:
        raise ValueError(f"Không tìm thấy nội dung văn bản trong file: {filepath}")

    return text


def prepare_speech_text(filepath: str, raw_text: str) -> str:
    """Convert format-specific content into text suitable for TTS."""
    extension = os.path.splitext(filepath)[1].lower()
    if extension == ".md":
        return parse_markdown_tables(raw_text)
    return raw_text


def _read_text_file(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as document:
        return document.read()


def _read_pdf_text(filepath: str) -> str:
    pages = []

    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                pages.append(page_text)

    extracted_text = "\n\n".join(pages)
    return clean_pdf_text_structure(extracted_text)


def main() -> int:
    """Print extracted document text for inspection."""
    argument_parser = argparse.ArgumentParser(
        description="Đọc và hiển thị nội dung văn bản của tài liệu."
    )
    argument_parser.add_argument(
        "input_file",
        help="Đường dẫn file đầu vào (.md, .pdf hoặc .txt)",
    )
    arguments = argument_parser.parse_args()

    try:
        print(read_document_text(arguments.input_file))
    except Exception as error:
        print(
            f"Không thể đọc file '{arguments.input_file}'. Lý do: {error}",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
