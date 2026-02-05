#!/usr/bin/env python3
"""
md-to-html — Markdown to HTML converter with A4 CSS presets.

Converts Markdown files into styled HTML documents using selectable
CSS themes (Official, GitHub, Claude). Supports both local files and URLs.

Usage:
    python3 md-to-html.py
"""

import os
import sys
import re
import html
import urllib.request
import urllib.error
from pathlib import Path

# ---------------------------------------------------------------------------
# Resolve paths relative to this script's location
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
CSS_DIR = SCRIPT_DIR / "css"
DEFAULT_INPUT_DIR = SCRIPT_DIR / "input_markdown"
DEFAULT_OUTPUT_DIR = SCRIPT_DIR / "output_html"

# Available CSS presets (file stem → display label)
CSS_PRESETS = {
    "A4_official": "A4 Official — Formal serif document (Times New Roman, corporate layout)",
    "A4_github": "A4 GitHub  — GitHub-flavored markdown style (system sans-serif)",
    "A4_claude": "A4 Claude  — Anthropic / Claude style (warm tones, modern sans-serif)",
}


# ============================================================================
#  Markdown → HTML converter
# ============================================================================

class MarkdownConverter:
    """A self-contained Markdown-to-HTML converter (no external dependencies).

    Supports: headings, paragraphs, bold, italic, bold-italic, strikethrough,
    inline code, code blocks (fenced & indented), blockquotes, ordered &
    unordered lists (nested), horizontal rules, links, images, tables,
    and task-list checkboxes.
    """

    # -- Regex patterns -------------------------------------------------------
    FENCED_CODE = re.compile(
        r"^(`{3,}|~{3,})\s*([\w+-]*)\s*\n(.*?)\n\1\s*$",
        re.MULTILINE | re.DOTALL,
    )

    TABLE_ROW = re.compile(r"^\|(.+)\|\s*$")
    TABLE_SEP = re.compile(r"^\|[\s:|-]+\|\s*$")

    HEADING = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
    HR = re.compile(r"^(?:[-*_]\s*){3,}$", re.MULTILINE)
    BLOCKQUOTE = re.compile(r"^(>\s?.*)(?:\n(?:>\s?.*))*", re.MULTILINE)

    UL_ITEM = re.compile(r"^([ \t]*)[-*+]\s+(.*)", re.MULTILINE)
    OL_ITEM = re.compile(r"^([ \t]*)\d+\.\s+(.*)", re.MULTILINE)

    LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

    BOLD_ITALIC = re.compile(r"\*{3}(.+?)\*{3}|_{3}(.+?)_{3}")
    BOLD = re.compile(r"\*{2}(.+?)\*{2}|_{2}(.+?)_{2}")
    ITALIC = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)|(?<!_)_(?!_)(.+?)(?<!_)_(?!_)")
    STRIKETHROUGH = re.compile(r"~~(.+?)~~")
    INLINE_CODE = re.compile(r"`([^`\n]+?)`")

    TASK_CHECKED = re.compile(r"^\[x\]\s*", re.IGNORECASE)
    TASK_UNCHECKED = re.compile(r"^\[ \]\s*")

    def convert(self, md_text: str) -> str:
        """Convert a Markdown string to an HTML body fragment."""
        text = md_text.replace("\r\n", "\n").replace("\r", "\n")

        # 1. Fenced code blocks (protect from further processing)
        code_blocks: list[str] = []
        text = self._extract_fenced_code(text, code_blocks)

        # 2. Tables
        text = self._convert_tables(text)

        # 3. Block-level elements
        text = self._convert_blockquotes(text)
        text = self._convert_headings(text)
        text = self._convert_hr(text)
        text = self._convert_lists(text)

        # 4. Inline elements
        text = self._convert_images(text)
        text = self._convert_links(text)
        text = self._convert_inline_formatting(text)

        # 5. Paragraphs
        text = self._convert_paragraphs(text)

        # 6. Restore code blocks
        text = self._restore_code_blocks(text, code_blocks)

        return text.strip()

    # -- Fenced code blocks ---------------------------------------------------

    def _extract_fenced_code(self, text: str, store: list[str]) -> str:
        def _replace(m: re.Match) -> str:
            lang = m.group(2)
            code = html.escape(m.group(3))
            lang_attr = f' class="language-{lang}"' if lang else ""
            block = f"<pre><code{lang_attr}>{code}</code></pre>"
            placeholder = f"\x00CODEBLOCK{len(store)}\x00"
            store.append(block)
            return placeholder
        return self.FENCED_CODE.sub(_replace, text)

    def _restore_code_blocks(self, text: str, store: list[str]) -> str:
        for i, block in enumerate(store):
            text = text.replace(f"\x00CODEBLOCK{i}\x00", block)
        return text

    # -- Tables ---------------------------------------------------------------

    def _convert_tables(self, text: str) -> str:
        lines = text.split("\n")
        result: list[str] = []
        i = 0
        while i < len(lines):
            if (
                i + 2 < len(lines)
                and self.TABLE_ROW.match(lines[i])
                and self.TABLE_SEP.match(lines[i + 1])
            ):
                # Parse alignment from separator row
                sep_cells = [c.strip() for c in lines[i + 1].strip().strip("|").split("|")]
                alignments: list[str] = []
                for cell in sep_cells:
                    if cell.startswith(":") and cell.endswith(":"):
                        alignments.append("center")
                    elif cell.endswith(":"):
                        alignments.append("right")
                    else:
                        alignments.append("left")

                # Header
                headers = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                table_html = "<table>\n<thead>\n<tr>\n"
                for idx, h in enumerate(headers):
                    align = alignments[idx] if idx < len(alignments) else "left"
                    h = self._inline(h)
                    table_html += f'<th style="text-align:{align}">{h}</th>\n'
                table_html += "</tr>\n</thead>\n<tbody>\n"

                # Body rows
                j = i + 2
                while j < len(lines) and self.TABLE_ROW.match(lines[j]):
                    cols = [c.strip() for c in lines[j].strip().strip("|").split("|")]
                    table_html += "<tr>\n"
                    for idx, col in enumerate(cols):
                        align = alignments[idx] if idx < len(alignments) else "left"
                        col = self._inline(col)
                        table_html += f'<td style="text-align:{align}">{col}</td>\n'
                    table_html += "</tr>\n"
                    j += 1

                table_html += "</tbody>\n</table>"
                result.append(table_html)
                i = j
            else:
                result.append(lines[i])
                i += 1
        return "\n".join(result)

    # -- Blockquotes ----------------------------------------------------------

    def _convert_blockquotes(self, text: str) -> str:
        def _replace(m: re.Match) -> str:
            inner = re.sub(r"^>\s?", "", m.group(0), flags=re.MULTILINE)
            inner = self._convert_blockquotes(inner)
            inner = self._convert_inline_formatting(inner)
            # Wrap bare lines in <p>
            paragraphs = re.split(r"\n{2,}", inner.strip())
            body = "\n".join(
                line if line.startswith("<") else f"<p>{line}</p>"
                for line in paragraphs
            )
            return f"<blockquote>\n{body}\n</blockquote>"
        return self.BLOCKQUOTE.sub(_replace, text)

    # -- Headings -------------------------------------------------------------

    def _convert_headings(self, text: str) -> str:
        def _replace(m: re.Match) -> str:
            level = len(m.group(1))
            content = self._inline(m.group(2).strip())
            slug = re.sub(r"[^\w\s-]", "", m.group(2).strip().lower())
            slug = re.sub(r"[\s]+", "-", slug)
            return f'<h{level} id="{slug}">{content}</h{level}>'
        return self.HEADING.sub(_replace, text)

    # -- Horizontal rules -----------------------------------------------------

    def _convert_hr(self, text: str) -> str:
        return self.HR.sub("<hr>", text)

    # -- Lists ----------------------------------------------------------------

    def _convert_lists(self, text: str) -> str:
        text = self._convert_list_block(text, ordered=False)
        text = self._convert_list_block(text, ordered=True)
        return text

    def _convert_list_block(self, text: str, ordered: bool) -> str:
        pattern = self.OL_ITEM if ordered else self.UL_ITEM
        tag = "ol" if ordered else "ul"

        lines = text.split("\n")
        result: list[str] = []
        list_items: list[str] = []
        in_list = False

        for line in lines:
            m = pattern.match(line)
            if m:
                if not in_list:
                    in_list = True
                content = m.group(2)
                content = self._convert_task_checkbox(content)
                content = self._inline(content)
                list_items.append(f"<li>{content}</li>")
            else:
                if in_list:
                    result.append(f"<{tag}>\n" + "\n".join(list_items) + f"\n</{tag}>")
                    list_items = []
                    in_list = False
                result.append(line)

        if in_list:
            result.append(f"<{tag}>\n" + "\n".join(list_items) + f"\n</{tag}>")

        return "\n".join(result)

    def _convert_task_checkbox(self, text: str) -> str:
        if self.TASK_CHECKED.match(text):
            return self.TASK_CHECKED.sub(
                '<input type="checkbox" checked disabled> ', text
            )
        if self.TASK_UNCHECKED.match(text):
            return self.TASK_UNCHECKED.sub(
                '<input type="checkbox" disabled> ', text
            )
        return text

    # -- Images & Links -------------------------------------------------------

    def _convert_images(self, text: str) -> str:
        return self.IMAGE.sub(
            lambda m: f'<img src="{m.group(2)}" alt="{html.escape(m.group(1))}">', text
        )

    def _convert_links(self, text: str) -> str:
        return self.LINK.sub(
            lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', text
        )

    # -- Inline formatting ----------------------------------------------------

    def _convert_inline_formatting(self, text: str) -> str:
        text = self.BOLD_ITALIC.sub(lambda m: f"<strong><em>{m.group(1) or m.group(2)}</em></strong>", text)
        text = self.BOLD.sub(lambda m: f"<strong>{m.group(1) or m.group(2)}</strong>", text)
        text = self.ITALIC.sub(lambda m: f"<em>{m.group(1) or m.group(2)}</em>", text)
        text = self.STRIKETHROUGH.sub(r"<del>\1</del>", text)
        text = self.INLINE_CODE.sub(lambda m: f"<code>{html.escape(m.group(1))}</code>", text)
        return text

    def _inline(self, text: str) -> str:
        """Apply all inline transformations to a string."""
        text = self._convert_images(text)
        text = self._convert_links(text)
        text = self._convert_inline_formatting(text)
        return text

    # -- Paragraphs -----------------------------------------------------------

    def _convert_paragraphs(self, text: str) -> str:
        blocks = re.split(r"\n{2,}", text)
        result: list[str] = []
        block_tags = (
            "<h", "<p", "<ul", "<ol", "<li", "<table", "<blockquote",
            "<pre", "<hr", "<div", "<details", "<figure",
        )
        for block in blocks:
            stripped = block.strip()
            if not stripped:
                continue
            if stripped.startswith(block_tags):
                result.append(stripped)
            elif "\x00CODEBLOCK" in stripped:
                result.append(stripped)
            else:
                # Convert single newlines to <br> inside paragraphs
                inner = stripped.replace("\n", "<br>\n")
                result.append(f"<p>{inner}</p>")
        return "\n\n".join(result)


# ============================================================================
#  Terminal UI helpers
# ============================================================================

COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "green": "\033[32m",
    "cyan": "\033[36m",
    "yellow": "\033[33m",
    "red": "\033[31m",
    "magenta": "\033[35m",
    "blue": "\033[34m",
    "underline": "\033[4m",
}


def c(text: str, *styles: str) -> str:
    """Wrap text in ANSI colour codes."""
    prefix = "".join(COLORS.get(s, "") for s in styles)
    return f"{prefix}{text}{COLORS['reset']}"


def banner() -> None:
    print()
    print(c("=" * 62, "cyan"))
    print(c("  MD-TO-HTML  ", "bold", "cyan") + c("— Markdown to Styled HTML Converter", "cyan"))
    print(c("=" * 62, "cyan"))
    print()


def section(title: str) -> None:
    print(c(f"\n--- {title} ---", "bold", "yellow"))


def prompt_input(label: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        value = input(c(f"  {label}{suffix}: ", "green")).strip()
    except (EOFError, KeyboardInterrupt):
        print("\nAborted.")
        sys.exit(0)
    return value if value else default


def prompt_choice(label: str, options: list[str]) -> int:
    print(c(f"\n  {label}", "green"))
    for i, opt in enumerate(options, 1):
        print(c(f"    [{i}] ", "bold", "cyan") + opt)
    while True:
        raw = prompt_input("Enter choice number")
        try:
            idx = int(raw)
            if 1 <= idx <= len(options):
                return idx - 1
        except ValueError:
            pass
        print(c("    Invalid choice. Try again.", "red"))


# ============================================================================
#  File / URL helpers
# ============================================================================

def read_url(url: str) -> str:
    """Download text content from a URL."""
    req = urllib.request.Request(url, headers={"User-Agent": "md-to-html/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        encoding = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(encoding)


def list_md_files(directory: Path) -> list[Path]:
    """Return sorted list of .md files in a directory."""
    if not directory.is_dir():
        return []
    return sorted(directory.glob("*.md"))


def build_html_document(title: str, css_content: str, body_html: str) -> str:
    """Wrap body HTML in a full HTML5 document with embedded CSS."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)}</title>
    <style>
{css_content}
    </style>
</head>
<body>
{body_html}
</body>
</html>
"""


# ============================================================================
#  Main workflow
# ============================================================================

def main() -> None:
    banner()

    converter = MarkdownConverter()

    # ---- Step 1: Markdown source -------------------------------------------
    section("Step 1 — Select Markdown Source")

    md_path_or_url = prompt_input(
        "Enter path or URL to a .md file (leave blank to browse local files)"
    )

    md_text: str = ""
    source_name: str = ""

    if md_path_or_url:
        if md_path_or_url.startswith(("http://", "https://")):
            # URL input
            print(c(f"  Downloading: {md_path_or_url}", "dim"))
            try:
                md_text = read_url(md_path_or_url)
                source_name = md_path_or_url.split("/")[-1]
                if not source_name.endswith(".md"):
                    source_name += ".md"
            except (urllib.error.URLError, urllib.error.HTTPError, OSError) as exc:
                print(c(f"  Error fetching URL: {exc}", "red"))
                sys.exit(1)
        else:
            # Local file path
            p = Path(md_path_or_url).expanduser().resolve()
            if not p.is_file():
                print(c(f"  File not found: {p}", "red"))
                sys.exit(1)
            md_text = p.read_text(encoding="utf-8")
            source_name = p.name
    else:
        # Browse input_markdown/
        md_files = list_md_files(DEFAULT_INPUT_DIR)
        if not md_files:
            print(c("  No .md files found in input_markdown/. Provide a path or URL.", "red"))
            sys.exit(1)
        idx = prompt_choice(
            "Select a Markdown file from input_markdown/:",
            [f.name for f in md_files],
        )
        chosen = md_files[idx]
        md_text = chosen.read_text(encoding="utf-8")
        source_name = chosen.name
        print(c(f"  Selected: {source_name}", "dim"))

    # ---- Step 2: Output folder ---------------------------------------------
    section("Step 2 — Output Folder")

    out_dir_input = prompt_input(
        "Enter output folder path (leave blank for output_html/)"
    )

    if out_dir_input:
        out_dir = Path(out_dir_input).expanduser().resolve()
    else:
        out_dir = DEFAULT_OUTPUT_DIR

    out_dir.mkdir(parents=True, exist_ok=True)
    print(c(f"  Output folder: {out_dir}", "dim"))

    # ---- Step 3: CSS preset ------------------------------------------------
    section("Step 3 — Choose HTML Style Preset")

    preset_keys = list(CSS_PRESETS.keys())
    preset_labels = list(CSS_PRESETS.values())
    idx = prompt_choice("Select a CSS theme:", preset_labels)
    chosen_preset = preset_keys[idx]

    css_file = CSS_DIR / f"{chosen_preset}.css"
    if not css_file.is_file():
        print(c(f"  CSS file not found: {css_file}", "red"))
        sys.exit(1)
    css_content = css_file.read_text(encoding="utf-8")
    print(c(f"  Theme: {chosen_preset}", "dim"))

    # ---- Step 4: Convert & write -------------------------------------------
    section("Step 4 — Converting")

    body_html = converter.convert(md_text)
    title = Path(source_name).stem.replace("_", " ").replace("-", " ").title()
    full_html = build_html_document(title, css_content, body_html)

    out_filename = Path(source_name).stem + "-" + chosen_preset + ".html"
    out_path = out_dir / out_filename
    out_path.write_text(full_html, encoding="utf-8")

    # ---- Done --------------------------------------------------------------
    print()
    print(c("=" * 62, "cyan"))
    print(c("  DONE!", "bold", "green"))
    print(c(f"  Source : {source_name}", "dim"))
    print(c(f"  Theme  : {chosen_preset}", "dim"))
    print(c(f"  Output : {out_path}", "dim"))
    file_size = out_path.stat().st_size
    if file_size < 1024:
        size_str = f"{file_size} B"
    else:
        size_str = f"{file_size / 1024:.1f} KB"
    print(c(f"  Size   : {size_str}", "dim"))
    print(c("=" * 62, "cyan"))
    print()


if __name__ == "__main__":
    main()
