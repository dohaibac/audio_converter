"""Convert Markdown (especially tables) into natural speakable Vietnamese text."""

from __future__ import annotations

from markdown_it import MarkdownIt

_md = MarkdownIt("commonmark").enable("table")


def _inline_text(token) -> str:
    """Flatten an inline token (and its children) to plain text."""
    if token.type == "text":
        return token.content
    if token.type == "code_inline":
        return token.content
    if token.type == "softbreak" or token.type == "hardbreak":
        return " "
    if token.children:
        return "".join(_inline_text(child) for child in token.children)
    return token.content or ""


def _render_table(tokens: list, start: int) -> tuple[str, int]:
    """
    Convert a markdown-it table token block into spoken Vietnamese text.
    Returns (spoken_text, index_after_table_close).
    """
    headers: list[str] = []
    rows: list[list[str]] = []
    current_row: list[str] = []
    in_header = False
    i = start

    while i < len(tokens):
        token = tokens[i]
        t = token.type

        if t == "thead_open":
            in_header = True
        elif t == "thead_close":
            in_header = False
        elif t == "tr_open":
            current_row = []
        elif t == "tr_close":
            if in_header:
                headers = current_row
            else:
                rows.append(current_row)
        elif t in ("th_open", "td_open"):
            # Next token is usually inline with cell content
            if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                current_row.append(_inline_text(tokens[i + 1]).strip())
                i += 1
        elif t == "table_close":
            break

        i += 1

    parts: list[str] = []
    header_label = ", ".join(headers) if headers else "không xác định"
    parts.append(f"\n[Bắt đầu dữ liệu bảng gồm các cột: {header_label}]\n")

    for row in rows:
        row_data = []
        for idx, cell in enumerate(row):
            header = headers[idx] if idx < len(headers) else f"Cột {idx + 1}"
            cell_text = cell.rstrip(" .")
            row_data.append(f"{header} là: {cell_text}")
        parts.append(f"Dòng tiếp theo: {', '.join(row_data)}.")

    parts.append("\n[Kết thúc dữ liệu bảng]\n")
    return "\n".join(parts), i


def markdown_to_speech_text(text: str) -> str:
    """
    Parse Markdown with markdown-it-py and return plain text optimized for TTS.
    Tables become natural spoken sentences; headings and emphasis are flattened.
    """
    tokens = _md.parse(text)
    parts: list[str] = []
    i = 0

    while i < len(tokens):
        token = tokens[i]
        t = token.type

        if t == "table_open":
            spoken, i = _render_table(tokens, i)
            parts.append(spoken)
        elif t == "heading_open":
            # Collect inline content of the heading, then skip until heading_close
            if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                level = token.tag  # h1, h2, ...
                title = _inline_text(tokens[i + 1]).strip()
                parts.append(f"\n{title}.\n")
                i += 1
            while i < len(tokens) and tokens[i].type != "heading_close":
                i += 1
        elif t == "paragraph_open":
            if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                parts.append(_inline_text(tokens[i + 1]).strip())
                i += 1
            while i < len(tokens) and tokens[i].type != "paragraph_close":
                i += 1
        elif t == "bullet_list_open" or t == "ordered_list_open":
            pass  # markers handled per list_item
        elif t == "list_item_open":
            # Find inline inside nested paragraph
            j = i + 1
            item_bits: list[str] = []
            while j < len(tokens) and tokens[j].type != "list_item_close":
                if tokens[j].type == "inline":
                    item_bits.append(_inline_text(tokens[j]).strip())
                j += 1
            if item_bits:
                parts.append(" ".join(item_bits) + ".")
            i = j
        elif t == "fence" or t == "code_block":
            code = (token.content or "").strip()
            if code:
                parts.append(f"Đoạn mã: {code}")
        elif t == "hr":
            parts.append(".")
        elif t == "blockquote_open":
            pass
        elif t == "html_block" or t == "html_inline":
            # Skip HTML comments / raw HTML (e.g. <!-- adf:table ... -->)
            pass

        i += 1

    # Collapse excess blank lines for cleaner TTS chunks
    lines = [line.rstrip() for line in "\n".join(parts).splitlines()]
    cleaned: list[str] = []
    blank = False
    for line in lines:
        if not line.strip():
            if not blank:
                cleaned.append("")
            blank = True
        else:
            cleaned.append(line)
            blank = False
    return "\n".join(cleaned).strip()


def parse_markdown_tables(text: str) -> str:
    """
    Convert Markdown tables (and surrounding Markdown) into speakable text.
    Kept as the public name used by md_app.py.
    """
    return markdown_to_speech_text(text)
