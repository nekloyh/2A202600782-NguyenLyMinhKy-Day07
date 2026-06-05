#!/usr/bin/env python3
"""Convert a PDF file to a readable Markdown document.

Default usage converts:
    ex_data/Lịch sử Deep Learning.pdf

The script uses the local `pdftotext` command when available because it keeps
Vietnamese spacing more accurately for this PDF. If `pdftotext` is not
installed, it falls back to optional Python packages such as PyMuPDF or pypdf.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_INPUT = Path("ex_data/Lịch sử Deep Learning.pdf")


def extract_with_pdftotext(pdf_path: Path) -> str:
    """Extract PDF text through Poppler's pdftotext."""
    pdftotext = shutil.which("pdftotext")
    if not pdftotext:
        raise RuntimeError("pdftotext is not installed")

    result = subprocess.run(
        [
            pdftotext,
            "-layout",
            "-nopgbrk",
            "-enc",
            "UTF-8",
            str(pdf_path),
            "-",
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.decode("utf-8", errors="replace")


def extract_with_pymupdf(pdf_path: Path) -> str:
    """Fallback extractor using PyMuPDF, if installed."""
    try:
        import fitz  # type: ignore
    except ImportError as exc:
        raise RuntimeError("PyMuPDF is not installed") from exc

    pages: list[str] = []
    with fitz.open(str(pdf_path)) as document:
        for page in document:
            pages.append(page.get_text("text"))
    return "\n\n".join(pages)


def extract_with_pypdf(pdf_path: Path) -> str:
    """Fallback extractor using pypdf, if installed."""
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError as exc:
        raise RuntimeError("pypdf is not installed") from exc

    reader = PdfReader(str(pdf_path))
    return "\n\n".join(page.extract_text() or "" for page in reader.pages)


def extract_pdf_text(pdf_path: Path) -> str:
    errors: list[str] = []
    for extractor in (extract_with_pdftotext, extract_with_pymupdf, extract_with_pypdf):
        try:
            return extractor(pdf_path)
        except Exception as exc:  # Keep trying the next extractor.
            errors.append(f"{extractor.__name__}: {exc}")

    details = "\n".join(f"- {error}" for error in errors)
    raise RuntimeError(
        "Could not extract PDF text. Install poppler-utils, PyMuPDF, or pypdf.\n"
        f"{details}"
    )


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\f", "\n\n")
    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)
    return text


def merge_known_wrapped_headings(lines: list[str]) -> list[str]:
    """Repair headings that are split by PDF line wrapping."""
    merged: list[str] = []
    i = 0
    while i < len(lines):
        current = lines[i].strip()
        next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""

        if (
            current == "Các Papers Nổi Tiếng và Quan Trọng Trong Lịch"
            and next_line == "Sử Deep Learning"
        ):
            merged.append("Các Papers Nổi Tiếng và Quan Trọng Trong Lịch Sử Deep Learning")
            i += 2
            continue

        merged.append(lines[i])
        i += 1

    return merged


def normalize_inline(text: str) -> str:
    text = re.sub(r"\s+", " ", text.strip())
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    text = re.sub(r"\[\s*(\d+)\s*\]", r"[\1]", text)
    return text


def is_reference_line(line: str) -> re.Match[str] | None:
    return re.match(r"^\s*(\d+)\.\s+((?:https?://|education\.|www\.).+)$", line)


def is_numbered_heading(line: str) -> bool:
    return bool(re.match(r"^\d+\.\s+\S", line)) and not is_reference_line(line)


def is_paper_title(line: str) -> bool:
    return bool(re.match(r'^".+"\s*\(\d{4}\)$', line))


def is_section_heading(line: str) -> bool:
    if not line or is_reference_line(line) or is_numbered_heading(line):
        return False
    if line.endswith((".", ":", ";", ",", "!", "?")):
        return False
    if len(line) > 100:
        return False

    heading_prefixes = (
        "Giai đoạn",
        "Ý tưởng",
        "Sự phát triển",
        "Thời kỳ",
        "Các Model",
        "Nhân tố",
        "Các Papers",
        "VGG Networks",
        "Contributions",
    )
    return line.startswith(heading_prefixes)


def starts_new_list_item(stripped: str, active_item: str | None) -> bool:
    if active_item is None:
        return True
    if not stripped:
        return False
    if active_item.rstrip().endswith(
        (
            " của",
            " và",
            " với",
            " cho",
            " từ",
            " về",
            " bằng",
            " trong",
            " theo",
            " như",
            " trò",
        )
    ):
        return False
    return stripped[0].isupper() or stripped[0].isdigit() or stripped[0] in {'"', "'"}


def starts_logical_paragraph(stripped: str) -> bool:
    if stripped.endswith(":") and stripped[0].isupper():
        return True
    if re.match(r"^Năm\s+\d{4},", stripped):
        return True

    paragraph_prefixes = (
        "Ứng dụng",
        "Kiến trúc",
        "Các kiến trúc",
        "Cấu trúc",
        "Biến thể",
    )
    return stripped.startswith(paragraph_prefixes)


def markdown_from_text(text: str) -> str:
    lines = merge_known_wrapped_headings(clean_text(text).splitlines())
    blocks: list[tuple[str, str]] = []
    paragraph: list[str] = []
    active_item: dict[str, str] | None = None
    title_seen = False
    references_heading_added = False

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            blocks.append(("paragraph", normalize_inline(" ".join(paragraph))))
            paragraph = []

    def flush_item() -> None:
        nonlocal active_item
        if active_item is None:
            return

        kind = active_item["kind"]
        if kind == "ordered":
            text = normalize_inline(active_item["text"])
            blocks.append(("ordered", f'{active_item["prefix"]} {text}'))
        else:
            text = normalize_inline(active_item["text"])
            blocks.append(("bullet", f"- {text}"))
        active_item = None

    for raw_line in lines:
        stripped = raw_line.strip()
        indent = len(raw_line) - len(raw_line.lstrip(" \t"))

        if not stripped:
            flush_item()
            flush_paragraph()
            continue

        if stripped == "⁂":
            flush_item()
            flush_paragraph()
            blocks.append(("hr", "---"))
            continue

        reference = is_reference_line(raw_line)
        if reference:
            flush_item()
            flush_paragraph()
            if not references_heading_added:
                blocks.append(("heading2", "## Nguồn tham khảo"))
                references_heading_added = True
            active_item = {
                "kind": "ordered",
                "prefix": f"{reference.group(1)}.",
                "text": reference.group(2),
            }
            continue

        if active_item and active_item["kind"] == "ordered" and indent > 0:
            active_item["text"] += stripped
            continue

        if not title_seen:
            flush_item()
            flush_paragraph()
            blocks.append(("heading1", f"# {normalize_inline(stripped)}"))
            title_seen = True
            continue

        if is_numbered_heading(stripped):
            flush_item()
            flush_paragraph()
            blocks.append(("heading3", f"### {normalize_inline(stripped)}"))
            continue

        if is_paper_title(stripped):
            flush_item()
            flush_paragraph()
            blocks.append(("heading3", f"### {normalize_inline(stripped)}"))
            continue

        if is_section_heading(stripped):
            flush_item()
            flush_paragraph()
            prefix = "###" if stripped.startswith("VGG Networks") else "##"
            blocks.append(("heading2", f"{prefix} {normalize_inline(stripped)}"))
            continue

        if indent > 0:
            flush_paragraph()
            if active_item and not starts_new_list_item(stripped, active_item["text"]):
                active_item["text"] += f" {stripped}"
            else:
                flush_item()
                active_item = {"kind": "bullet", "text": stripped}
            continue

        flush_item()
        if paragraph and starts_logical_paragraph(stripped):
            flush_paragraph()
        paragraph.append(stripped)

    flush_item()
    flush_paragraph()

    return render_blocks(blocks)


def render_blocks(blocks: list[tuple[str, str]]) -> str:
    rendered: list[str] = []
    previous_kind: str | None = None

    for kind, text in blocks:
        if kind in {"heading1", "heading2", "heading3", "paragraph", "hr"}:
            if rendered and rendered[-1] != "":
                rendered.append("")
            rendered.append(text)
            rendered.append("")
        elif kind in {"bullet", "ordered"}:
            if previous_kind not in {"bullet", "ordered"} and rendered and rendered[-1] != "":
                rendered.append("")
            rendered.append(text)

        previous_kind = kind

    while rendered and rendered[-1] == "":
        rendered.pop()

    return "\n".join(rendered) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert a PDF file to Markdown.")
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"PDF input path. Default: {DEFAULT_INPUT}",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Markdown output path. Default: same folder and stem as input.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pdf_path = args.input
    output_path = args.output or pdf_path.with_suffix(".md")

    if not pdf_path.exists():
        print(f"Input PDF not found: {pdf_path}", file=sys.stderr)
        return 1

    text = extract_pdf_text(pdf_path)
    markdown = markdown_from_text(text)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")

    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
